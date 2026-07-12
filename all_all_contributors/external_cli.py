import os
import shutil
import subprocess
import sys
from pathlib import Path


class ExternalCLIError(Exception):
    """Raised when an external CLI subprocess exits non-zero."""

    def __init__(self, command: str, stderr: str):
        self.command = command
        self.stderr = stderr
        super().__init__(f"{command} failed: {stderr}")


class GitCLI:
    """Thin wrapper around local git CLI commands."""

    def __init__(self, repo_dir: str = "."):
        self.repo_dir = Path(repo_dir)

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        """Run a git command, raise ExternalCLIError on non-zero exit."""
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            cwd=self.repo_dir,
        )

        if result.returncode != 0:
            raise ExternalCLIError(f"git {' '.join(args)}", result.stderr.strip())

        return result

    def verify_environment(self) -> None:
        """Check git is available, we're inside a repo, and committer identity is set."""
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError) as ex:
            print("Error: git must be installed and available on PATH", file=sys.stderr)
            raise SystemExit(1)

        # Mark repo_dir as safe to handle ownership mismatches in containers
        abs_repo = str(self.repo_dir.resolve())
        subprocess.run(
            ["git", "config", "--global", "--add", "safe.directory", abs_repo],
            capture_output=True,
            text=True,
        )

        if not (self.repo_dir / ".git").is_dir():
            print(
                "Error: target repository must be cloned locally before running this tool",
                file=sys.stderr,
            )
            raise SystemExit(1)

        # Ensure committer identity is configured (required for commits in CI)
        self._ensure_git_config("user.name", "all-all-contributors[bot]")
        self._ensure_git_config(
            "user.email", "all-all-contributors[bot]@users.noreply.github.com"
        )

    def _ensure_git_config(self, key: str, default: str) -> None:
        """Set a git config value if not already configured."""
        result = subprocess.run(
            ["git", "config", key],
            capture_output=True,
            text=True,
            cwd=self.repo_dir,
        )
        if result.returncode != 0 or not result.stdout.strip():
            self._run("config", "--global", key, default)

    def create_branch(self, head_branch: str, base_branch: str) -> None:
        """Create a new branch from base_branch, or switch to it if it already exists."""
        try:
            self._run("switch", "-c", head_branch, base_branch)
        except ExternalCLIError:
            # base_branch ref may not exist in shallow clones; try from HEAD
            try:
                self._run("switch", "-c", head_branch)
            except ExternalCLIError:
                # Branch already exists locally
                self._run("switch", head_branch)

    def check_for_changes(self) -> bool:
        """Return True if there are unstaged changes."""
        result = subprocess.run(
            ["git", "diff", "--quiet"],
            capture_output=True,
            text=True,
            cwd=self.repo_dir,
        )
        return result.returncode != 0

    def commit_file(
        self,
        filepath: str,
        message: str = "Merging all contributors info from across the org",
    ) -> None:
        self._run("add", filepath)
        self._run("commit", "-m", message)

    def push_branch(self, branch_name: str) -> None:
        """Push branch to origin, force-push if remote branch exists.

        Using both `--force` and `--set-upstream` handles both new and
        existing remote branches in one call.
        """
        self._run("push", "--set-upstream", "--force", "origin", branch_name)


def verify_all_contributors_environment() -> None:
    """Checks the binary is on PATH and executable first.

    Raises ExternalCLIError on any failure.
    """
    path = shutil.which("all-contributors")
    if path is None:
        raise ExternalCLIError(
            "which all-contributors", "all-contributors is not installed or not on PATH"
        )
    if not os.access(path, os.X_OK):
        raise ExternalCLIError(
            "", f"all-contributors lacks execute permissions: {path}"
        )


def run_all_contributors_generate(repo_dir: str = ".") -> None:
    """Run `all-contributors generate` in repo_dir.

    Raises ExternalCLIError on any failure.
    """
    try:
        result = subprocess.run(
            ["all-contributors", "generate"],
            capture_output=True,
            text=True,
            cwd=repo_dir,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        raise ExternalCLIError(
            "all-contributors generate",
            "all-contributors generate timed out after 30 seconds",
        )

    if result.returncode != 0:
        detail = result.stderr.strip() or f"exit code {result.returncode}"
        raise ExternalCLIError(
            "all-contributors generate", f"all-contributors generate failed: {detail}"
        )
