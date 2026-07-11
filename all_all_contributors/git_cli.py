import subprocess
import sys
from pathlib import Path


class GitCLIError(Exception):
    """Raised when a git subprocess exits non-zero."""
    def __init__(self, command: str, stderr: str):
        self.command = command
        self.stderr = stderr
        super().__init__(f"git {command} failed: {stderr}")


class GitCLI:
    """Thin wrapper around local git CLI commands."""

    def __init__(self, repo_dir: str = "."):
        self.repo_dir = Path(repo_dir)

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        """Run a git command, raise GitCLIError on non-zero exit."""
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            cwd=self.repo_dir,
        )
        
        if result.returncode != 0:
            raise GitCLIError(" ".join(args), result.stderr.strip())
        
        return result

    def verify_environment(self) -> None:
        """Check git is available and we're inside a repo."""
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError) as ex:
            print("Error: git must be installed and available on PATH", file=sys.stderr)
            raise SystemExit(1)

        if not (self.repo_dir / ".git").is_dir():
            print("Error: target repository must be cloned locally before running this tool", file=sys.stderr)
            raise SystemExit(1)

    def create_branch(self, head_branch: str, base_branch: str) -> None:
        """Create a new branch, or switch to it if it already exists."""
        try:
            self._run("switch", "-c", head_branch, base_branch)
        except GitCLIError:
            self._run("switch", head_branch)

    def check_for_changes(self) -> bool:
        """Return True if there are unstaged changes."""
        result = subprocess.run(
            ["git", "diff", "--quiet"],
            capture_output=True,
            text=True,
            cwd=self.repo_dir
        )
        return result.returncode != 0
