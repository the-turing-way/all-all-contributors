import subprocess
from unittest.mock import MagicMock, call, patch

import pytest

from all_all_contributors import git_operations


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
    def test_checks_out_existing_branch(self, mock_run):
        """Test that existing branch is checked out when create=False"""
        git_operations.checkout_branch(
            "existing-branch", create=False, working_dir="/test/repo"
        )

        mock_run.assert_called_once_with(
            ["git", "checkout", "existing-branch"],
            cwd="/test/repo",
            check=True,
            capture_output=True,
            text=True,
        )


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
