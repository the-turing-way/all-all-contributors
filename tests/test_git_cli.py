import subprocess
from unittest.mock import MagicMock, patch

import pytest

from all_all_contributors.git_cli import GitCLI, GitCLIError


class TestRun:
    @patch("subprocess.run")
    def test_non_zero_exit_raises(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["git", "status"], returncode=1, stdout="", stderr="something broke"
        )
        cli = GitCLI("/tmp/repo")
        with pytest.raises(GitCLIError) as exc_info:
            cli._run("status")
        assert exc_info.value.command == "status"
        assert exc_info.value.stderr == "something broke"


class TestVerifyEnvironment:
    @patch("subprocess.run")
    def test_success(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["git", "--version"],
            returncode=0,
            stdout="git version 2.40.0",
            stderr="",
        )
        cli = GitCLI(".")
        with patch.object(cli.repo_dir.__class__, "is_dir", return_value=True):
            # Patch the specific path object
            with patch("pathlib.Path.is_dir", return_value=True):
                cli.verify_environment()  # should not raise

    @patch("subprocess.run", side_effect=FileNotFoundError("git not found"))
    def test_git_not_installed_raises_system_exit(self, mock_run):
        cli = GitCLI(".")
        with pytest.raises(SystemExit) as exc_info:
            cli.verify_environment()
        assert exc_info.value.code == 1

    @patch("pathlib.Path.is_dir", return_value=False)
    @patch("subprocess.run")
    def test_missing_git_dir_raises_system_exit(self, mock_run, mock_is_dir):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["git", "--version"],
            returncode=0,
            stdout="git version 2.40.0",
            stderr="",
        )
        cli = GitCLI("/tmp/not-a-repo")
        with pytest.raises(SystemExit) as exc_info:
            cli.verify_environment()
        assert exc_info.value.code == 1


class TestCreateBranch:
    @patch("subprocess.run")
    def test_creates_new_branch(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        cli = GitCLI("/tmp/repo")
        cli.create_branch("feature", "main")
        mock_run.assert_called_once_with(
            ["git", "switch", "-c", "feature", "main"],
            capture_output=True,
            text=True,
            cwd=cli.repo_dir,
        )

    @patch("subprocess.run")
    def test_fallback_to_existing_branch(self, mock_run):
        """First call fails (branch exists), second call switches to it."""
        fail = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="already exists"
        )
        success = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        mock_run.side_effect = [fail, success]

        cli = GitCLI("/tmp/repo")
        cli.create_branch("feature", "main")

        assert mock_run.call_count == 2
        mock_run.assert_called_with(
            ["git", "switch", "feature"],
            capture_output=True,
            text=True,
            cwd=cli.repo_dir,
        )

    @patch("subprocess.run")
    def test_both_fail_raises(self, mock_run):
        fail = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="fatal"
        )
        mock_run.return_value = fail

        cli = GitCLI("/tmp/repo")
        with pytest.raises(GitCLIError):
            cli.create_branch("feature", "main")


class TestCommitFile:
    @patch("subprocess.run")
    def test_successful_commit(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        cli = GitCLI("/tmp/repo")
        cli.commit_file("README.md")  # should not raise

        assert mock_run.call_count == 2
        calls = mock_run.call_args_list
        assert calls[0][0][0] == ["git", "add", "README.md"]
        assert calls[1][0][0] == [
            "git",
            "commit",
            "-m",
            "Merging all contributors info from across the org",
        ]

    @patch("subprocess.run")
    def test_commit_failure_raises(self, mock_run):
        success = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        fail = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="nothing to commit"
        )
        mock_run.side_effect = [success, fail]

        cli = GitCLI("/tmp/repo")
        with pytest.raises(GitCLIError):
            cli.commit_file("README.md")


class TestPushBranch:
    @patch("subprocess.run")
    def test_push_correct_args(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        cli = GitCLI("/tmp/repo")
        cli.push_branch("feature")
        mock_run.assert_called_once_with(
            ["git", "push", "--set-upstream", "--force", "origin", "feature"],
            capture_output=True,
            text=True,
            cwd=cli.repo_dir,
        )

    @patch("subprocess.run")
    def test_push_failure_raises_with_stderr(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="permission denied"
        )
        cli = GitCLI("/tmp/repo")
        with pytest.raises(GitCLIError) as exc_info:
            cli.push_branch("feature")
        assert "permission denied" in exc_info.value.stderr


class TestEnsureGitConfig:
    @patch("subprocess.run")
    def test_sets_config_when_missing(self, mock_run):
        """If git config returns non-zero (unset), _ensure_git_config should set it."""
        not_set = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr=""
        )
        set_ok = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        mock_run.side_effect = [not_set, set_ok]

        cli = GitCLI("/tmp/repo")
        cli._ensure_git_config("user.name", "bot[bot]")

        assert mock_run.call_count == 2
        mock_run.assert_called_with(
            ["git", "config", "user.name", "bot[bot]"],
            capture_output=True,
            text=True,
            cwd=cli.repo_dir,
        )

    @patch("subprocess.run")
    def test_skips_when_already_set(self, mock_run):
        """If git config returns a value, _ensure_git_config should not overwrite it."""
        already_set = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="Existing User\n", stderr=""
        )
        mock_run.return_value = already_set

        cli = GitCLI("/tmp/repo")
        cli._ensure_git_config("user.name", "bot[bot]")

        mock_run.assert_called_once_with(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            cwd=cli.repo_dir,
        )


class TestCheckForChanges:
    @patch("subprocess.run")
    def test_no_changes(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        cli = GitCLI("/tmp/repo")
        assert cli.check_for_changes() is False

    @patch("subprocess.run")
    def test_has_changes(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr=""
        )
        cli = GitCLI("/tmp/repo")
        assert cli.check_for_changes() is True
