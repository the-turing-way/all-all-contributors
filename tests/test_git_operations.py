import subprocess
from unittest.mock import MagicMock, call, patch

import pytest

from all_all_contributors import git_operations


class TestConfigureSafeDirectory:
    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_configures_safe_directory(self, mock_run):
        """Test that git config safe.directory is called with absolute path"""
        git_operations.configure_safe_directory("/test/repo")

        # Should be called with absolute path
        mock_run.assert_called_once_with(
            ["git", "config", "--global", "--add", "safe.directory", "/test/repo"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_subprocess_error_is_raised(self, mock_run):
        """Test that subprocess errors are propagated"""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["git", "config"], stderr="error message"
        )

        with pytest.raises(subprocess.CalledProcessError):
            git_operations.configure_safe_directory("/test/repo")


class TestCheckoutBranch:
    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_creates_new_branch(self, mock_run):
        """Test that new branch is created when create=True"""
        git_operations.checkout_branch(
            "new-branch", create=True, working_dir="/test/repo"
        )

        mock_run.assert_called_once_with(
            ["git", "checkout", "-b", "new-branch"],
            cwd="/test/repo",
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_checks_out_existing_local_branch(self, mock_run):
        """Test that existing local branch is checked out when create=False"""
        git_operations.checkout_branch(
            "existing-branch", create=False, working_dir="/test/repo"
        )

        # Should first fetch, then checkout
        assert mock_run.call_count == 2
        mock_run.assert_any_call(
            ["git", "fetch", "origin", "existing-branch"],
            cwd="/test/repo",
            check=True,
            capture_output=True,
            text=True,
        )
        mock_run.assert_any_call(
            ["git", "checkout", "existing-branch"],
            cwd="/test/repo",
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_checks_out_remote_branch_when_local_fails(self, mock_run):
        """Test that remote branch is checked out when local checkout fails"""

        # First call is fetch (succeeds), second is checkout (fails), third is checkout --track (succeeds)
        def side_effect(*args, **kwargs):
            cmd = args[0]
            if cmd[0:2] == ["git", "fetch"]:
                return MagicMock()
            elif cmd[0:2] == ["git", "checkout"] and len(cmd) == 3:
                # Regular checkout fails
                raise subprocess.CalledProcessError(
                    1, cmd, stderr="pathspec did not match"
                )
            elif cmd[0:3] == ["git", "checkout", "--track"]:
                # Checkout with --track succeeds
                return MagicMock()

        mock_run.side_effect = side_effect

        git_operations.checkout_branch(
            "remote-branch", create=False, working_dir="/test/repo"
        )

        # Should fetch, try checkout, then checkout --track
        assert mock_run.call_count == 3
        calls = mock_run.call_args_list

        # First call: fetch
        assert calls[0] == call(
            ["git", "fetch", "origin", "remote-branch"],
            cwd="/test/repo",
            check=True,
            capture_output=True,
            text=True,
        )

        # Second call: checkout
        assert calls[1] == call(
            ["git", "checkout", "remote-branch"],
            cwd="/test/repo",
            check=True,
            capture_output=True,
            text=True,
        )

        # Third call: checkout --track
        assert calls[2] == call(
            ["git", "checkout", "--track", "origin/remote-branch"],
            cwd="/test/repo",
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_continues_after_fetch_failure(self, mock_run):
        """Test that checkout continues even if fetch fails"""

        # First call is fetch (fails), second is checkout (succeeds)
        def side_effect(*args, **kwargs):
            cmd = args[0]
            if cmd[0:2] == ["git", "fetch"]:
                raise subprocess.CalledProcessError(1, cmd, stderr="fetch failed")
            elif cmd[0:2] == ["git", "checkout"]:
                return MagicMock()

        mock_run.side_effect = side_effect

        git_operations.checkout_branch(
            "local-branch", create=False, working_dir="/test/repo"
        )

        # Should attempt fetch and checkout
        assert mock_run.call_count == 2


class TestStageModifiedFiles:
    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_stages_modified_files_only(self, mock_run):
        """Test that git add --update is executed"""
        git_operations.stage_modified_files("/test/repo")

        mock_run.assert_called_once_with(
            ["git", "add", "--update"],
            cwd="/test/repo",
            check=True,
            capture_output=True,
            text=True,
        )


class TestHasChanges:
    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_returns_true_when_changes_exist(self, mock_run):
        """Test that function returns True when there are changes"""
        # git diff --quiet returns 1 when there are changes
        mock_run.return_value = MagicMock(returncode=1)

        result = git_operations.has_changes("/test/repo")

        assert result is True
        mock_run.assert_called_once_with(
            ["git", "diff", "--quiet"],
            cwd="/test/repo",
            capture_output=True,
            text=True,
        )

    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_returns_false_when_no_changes_exist(self, mock_run):
        """Test that function returns False when there are no changes"""
        # git diff --quiet returns 0 when there are no changes
        mock_run.return_value = MagicMock(returncode=0)

        result = git_operations.has_changes("/test/repo")

        assert result is False


class TestCreateCommit:
    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_creates_commit_with_message(self, mock_run):
        """Test that commit is created with proper message"""
        message = "Test commit message"
        git_operations.create_commit(message, "/test/repo")

        mock_run.assert_called_once_with(
            ["git", "commit", "-m", message],
            cwd="/test/repo",
            check=True,
            capture_output=True,
            text=True,
        )


class TestPushBranch:
    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_pushes_branch_to_remote(self, mock_run):
        """Test that branch is pushed to origin"""
        git_operations.push_branch("test-branch", "/test/repo")

        mock_run.assert_called_once_with(
            ["git", "push", "origin", "test-branch"],
            cwd="/test/repo",
            check=True,
            capture_output=True,
            text=True,
        )


class TestErrorHandling:
    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_subprocess_error_is_raised(self, mock_run):
        """Test that subprocess errors are propagated"""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["git", "commit"])

        with pytest.raises(subprocess.CalledProcessError):
            git_operations.create_commit("Test", "/test/repo")
