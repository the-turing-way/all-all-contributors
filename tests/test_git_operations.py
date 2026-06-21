import subprocess
from unittest.mock import MagicMock, call, patch

import pytest

from all_all_contributors import git_operations


class TestBranchExistsRemote:
    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_returns_true_when_branch_exists(self, mock_run):
        """Test that function returns True when branch exists on remote"""
        mock_run.return_value = MagicMock(stdout="abc123 refs/heads/test-branch\n")

        exists, branch_name = git_operations.branch_exists_remote("test-branch", "/test/repo")

        assert exists is True
        assert branch_name == "test-branch"
        mock_run.assert_called_once_with(
            ["git", "ls-remote", "--heads", "origin", "test-branch"],
            cwd="/test/repo",
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_returns_false_when_branch_does_not_exist(self, mock_run):
        """Test that function returns False when branch doesn't exist on remote"""
        mock_run.return_value = MagicMock(stdout="")

        exists, branch_name = git_operations.branch_exists_remote("test-branch", "/test/repo")

        assert exists is False
        assert branch_name == "test-branch"

    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_finds_existing_branch_with_prefix_pattern(self, mock_run):
        """Test that function finds existing branch when checking with prefix pattern"""
        # First call checks for prefix pattern, second is the fallback
        mock_run.side_effect = [
            MagicMock(stdout="def456\trefs/heads/merged-all-contributors/XyZw\n"),
        ]

        exists, branch_name = git_operations.branch_exists_remote(
            "merged-all-contributors/aBcD", "/test/repo"
        )

        assert exists is True
        assert branch_name == "merged-all-contributors/XyZw"
        mock_run.assert_called_once_with(
            ["git", "ls-remote", "--heads", "origin", "merged-all-contributors/*"],
            cwd="/test/repo",
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_returns_false_when_no_prefix_match_exists(self, mock_run):
        """Test that function returns False when no branch with prefix exists"""
        # Both prefix pattern check and exact match return empty
        mock_run.side_effect = [
            MagicMock(stdout=""),  # prefix pattern check
            MagicMock(stdout=""),  # exact match fallback
        ]

        exists, branch_name = git_operations.branch_exists_remote(
            "merged-all-contributors/aBcD", "/test/repo"
        )

        assert exists is False
        assert branch_name == "merged-all-contributors/aBcD"


class TestCheckoutBranch:
    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_creates_new_branch(self, mock_run):
        """Test that new branch is created when create=True"""
        git_operations.checkout_branch("new-branch", create=True, working_dir="/test/repo")

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


class TestPullLatest:
    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_pulls_latest_changes(self, mock_run):
        """Test that git pull is executed"""
        git_operations.pull_latest("/test/repo")

        mock_run.assert_called_once_with(
            ["git", "pull"],
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
