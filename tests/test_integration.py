"""Integration tests for error handling and workflow scenarios"""

import os
import subprocess
from unittest.mock import MagicMock, mock_open, patch

import pytest
import requests

from all_all_contributors import cli, git_operations, github_api


class TestGitErrorHandling:
    """Test that git command failures are handled properly"""

    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_checkout_fails_on_invalid_branch(self, mock_run):
        """Test that invalid branch checkout raises CalledProcessError"""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["git", "checkout"])

        with pytest.raises(subprocess.CalledProcessError):
            git_operations.checkout_branch(
                "nonexistent-branch", create=False, working_dir="/test/repo"
            )

    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_commit_fails_when_nothing_to_commit(self, mock_run):
        """Test that commit with no changes raises CalledProcessError"""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["git", "commit"])

        with pytest.raises(subprocess.CalledProcessError):
            git_operations.create_commit("test message", "/test/repo")

    @patch("all_all_contributors.git_operations.subprocess.run")
    def test_push_fails_on_permission_denied(self, mock_run):
        """Test that permission errors during push raise CalledProcessError"""
        mock_run.side_effect = subprocess.CalledProcessError(128, ["git", "push"])

        with pytest.raises(subprocess.CalledProcessError):
            git_operations.push_branch("test-branch", "/test/repo")


class TestGitHubAPIErrorHandling:
    """Test that GitHub API failures are handled properly"""

    @patch("all_all_contributors.github_api.get_request")
    def test_get_repos_fails_on_auth_error(self, mock_get):
        """Test that authentication errors during repo fetch raise HTTPError"""
        mock_get.side_effect = requests.HTTPError("401 Unauthorized")

        with pytest.raises(requests.HTTPError):
            github_api.get_all_repos("test-org", "bad-token", set())

    @patch("all_all_contributors.github_api.get_request")
    def test_get_contributors_handles_404_gracefully(self, mock_get):
        """Test that 404 errors return empty list instead of raising"""
        mock_get.side_effect = requests.HTTPError("404 Not Found")

        result = github_api.get_contributors_from_repo("test-org", "test-repo", "token")

        assert result == []

    @patch("all_all_contributors.github_api.get_request")
    def test_get_contributors_raises_on_500_error(self, mock_get):
        """Test that 5xx errors are not silently swallowed"""
        mock_get.side_effect = requests.HTTPError("500 Internal Server Error")

        with pytest.raises(requests.HTTPError):
            github_api.get_contributors_from_repo("test-org", "test-repo", "token")

    @patch("all_all_contributors.github_api.post_request")
    def test_create_pr_fails_on_validation_error(self, mock_post):
        """Test that PR creation validation errors raise HTTPError"""
        mock_post.side_effect = requests.HTTPError("422 Unprocessable Entity")

        with pytest.raises(requests.HTTPError):
            github_api.create_update_pull_request(
                "test-org",
                "test-repo",
                "main",
                "test-branch",
                pr_exists=False,
                pr_number=None,
                github_token="token",
            )


class TestWorkflowIntegration:
    """Test workflow scenarios with multiple components"""

    @patch.dict(os.environ, {"INPUT_GITHUB_TOKEN": "test-token"})
    @patch("all_all_contributors.cli.github_api.create_update_pull_request")
    @patch("all_all_contributors.cli.git_operations.push_branch")
    @patch("all_all_contributors.cli.git_operations.create_commit")
    @patch("all_all_contributors.cli.git_operations.has_changes")
    @patch("all_all_contributors.cli.git_operations.stage_modified_files")
    @patch("builtins.open", new_callable=mock_open, read_data='{"contributors": []}')
    @patch("all_all_contributors.cli.inject_config")
    @patch("all_all_contributors.cli.git_operations.checkout_branch")
    @patch("all_all_contributors.cli.github_api.find_existing_pull_request")
    @patch("all_all_contributors.cli.merge_contributors")
    @patch("all_all_contributors.cli.github_api.get_contributors_from_repo")
    @patch("all_all_contributors.cli.github_api.get_all_repos")
    @patch("all_all_contributors.cli.load_excluded_repos")
    @patch("all_all_contributors.cli.git_operations.configure_safe_directory")
    def test_workflow_handles_git_push_failure(
        self,
        mock_configure_safe,
        mock_load_excluded,
        mock_get_repos,
        mock_get_contributors,
        mock_merge,
        mock_find_pr,
        mock_checkout,
        mock_inject,
        mock_file,
        mock_stage,
        mock_has_changes,
        mock_commit,
        mock_push,
        mock_create_pr,
    ):
        """Test that push failures propagate and don't create PR"""
        # Setup mocks
        mock_load_excluded.return_value = set()
        mock_get_repos.return_value = ["repo1"]
        mock_get_contributors.return_value = [{"login": "user1"}]
        mock_merge.return_value = [{"login": "user1"}]
        mock_find_pr.return_value = (False, "test-branch", None)
        mock_inject.return_value = {"contributors": [{"login": "user1"}]}
        mock_has_changes.return_value = True

        # Make push fail
        mock_push.side_effect = subprocess.CalledProcessError(1, ["git", "push"])

        # Workflow should fail at push
        with pytest.raises(subprocess.CalledProcessError):
            cli.main(
                organisation="test-org",
                target_repo="test-repo",
                github_token="test-token",
                target_filepath=".all-contributorsrc",
                base_branch="main",
                head_branch="test-branch",
                working_dir="/test/repo",
            )

        # PR should not be created after push failure
        mock_create_pr.assert_not_called()

    @patch.dict(os.environ, {"INPUT_GITHUB_TOKEN": "test-token"})
    @patch("all_all_contributors.cli.github_api.create_update_pull_request")
    @patch("all_all_contributors.cli.git_operations.push_branch")
    @patch("all_all_contributors.cli.git_operations.create_commit")
    @patch("all_all_contributors.cli.git_operations.has_changes")
    @patch("all_all_contributors.cli.git_operations.stage_modified_files")
    @patch("builtins.open", new_callable=mock_open, read_data='{"contributors": []}')
    @patch("all_all_contributors.cli.inject_config")
    @patch("all_all_contributors.cli.git_operations.checkout_branch")
    @patch("all_all_contributors.cli.github_api.find_existing_pull_request")
    @patch("all_all_contributors.cli.merge_contributors")
    @patch("all_all_contributors.cli.github_api.get_contributors_from_repo")
    @patch("all_all_contributors.cli.github_api.get_all_repos")
    @patch("all_all_contributors.cli.load_excluded_repos")
    @patch("all_all_contributors.cli.git_operations.configure_safe_directory")
    def test_workflow_handles_commit_failure(
        self,
        mock_configure_safe,
        mock_load_excluded,
        mock_get_repos,
        mock_get_contributors,
        mock_merge,
        mock_find_pr,
        mock_checkout,
        mock_inject,
        mock_file,
        mock_stage,
        mock_has_changes,
        mock_commit,
        mock_push,
        mock_create_pr,
    ):
        """Test that commit failures propagate correctly"""
        # Setup mocks
        mock_load_excluded.return_value = set()
        mock_get_repos.return_value = ["repo1"]
        mock_get_contributors.return_value = [{"login": "user1"}]
        mock_merge.return_value = [{"login": "user1"}]
        mock_find_pr.return_value = (False, "test-branch", None)
        mock_inject.return_value = {"contributors": [{"login": "user1"}]}
        mock_has_changes.return_value = True

        # Make commit fail (e.g., nothing to commit)
        mock_commit.side_effect = subprocess.CalledProcessError(1, ["git", "commit"])

        # Workflow should fail at commit
        with pytest.raises(subprocess.CalledProcessError):
            cli.main(
                organisation="test-org",
                target_repo="test-repo",
                github_token="test-token",
                target_filepath=".all-contributorsrc",
                base_branch="main",
                head_branch="test-branch",
                working_dir="/test/repo",
            )

        # Push and PR creation should not happen after commit failure
        mock_push.assert_not_called()
        mock_create_pr.assert_not_called()

    @patch.dict(os.environ, {"INPUT_GITHUB_TOKEN": "bad-token"})
    @patch("all_all_contributors.cli.github_api.get_all_repos")
    @patch("all_all_contributors.cli.load_excluded_repos")
    @patch("all_all_contributors.cli.git_operations.configure_safe_directory")
    def test_workflow_handles_github_auth_failure(
        self, mock_configure_safe, mock_load_excluded, mock_get_repos
    ):
        """Test that GitHub authentication failures are propagated"""
        mock_load_excluded.return_value = set()
        mock_get_repos.side_effect = requests.HTTPError("401 Unauthorized")

        with pytest.raises(requests.HTTPError):
            cli.main(
                organisation="test-org",
                target_repo="test-repo",
                github_token="bad-token",
                target_filepath=".all-contributorsrc",
                base_branch="main",
                head_branch="test-branch",
                working_dir="/test/repo",
            )

    @patch.dict(os.environ, {"INPUT_GITHUB_TOKEN": "test-token"})
    @patch("all_all_contributors.cli.github_api.create_update_pull_request")
    @patch("all_all_contributors.cli.git_operations.push_branch")
    @patch("all_all_contributors.cli.git_operations.create_commit")
    @patch("all_all_contributors.cli.git_operations.has_changes")
    @patch("all_all_contributors.cli.git_operations.stage_modified_files")
    @patch("builtins.open", new_callable=mock_open, read_data='{"contributors": []}')
    @patch("all_all_contributors.cli.inject_config")
    @patch("all_all_contributors.cli.git_operations.checkout_branch")
    @patch("all_all_contributors.cli.github_api.find_existing_pull_request")
    @patch("all_all_contributors.cli.merge_contributors")
    @patch("all_all_contributors.cli.github_api.get_contributors_from_repo")
    @patch("all_all_contributors.cli.github_api.get_all_repos")
    @patch("all_all_contributors.cli.load_excluded_repos")
    @patch("all_all_contributors.cli.git_operations.configure_safe_directory")
    def test_workflow_completes_after_successful_push(
        self,
        mock_configure_safe,
        mock_load_excluded,
        mock_get_repos,
        mock_get_contributors,
        mock_merge,
        mock_find_pr,
        mock_checkout,
        mock_inject,
        mock_file,
        mock_stage,
        mock_has_changes,
        mock_commit,
        mock_push,
        mock_create_pr,
    ):
        """Test that PR is created after successful push"""
        # Setup all mocks to succeed
        mock_load_excluded.return_value = set()
        mock_get_repos.return_value = ["repo1"]
        mock_get_contributors.return_value = [{"login": "user1"}]
        mock_merge.return_value = [{"login": "user1"}]
        mock_find_pr.return_value = (False, "test-branch", None)
        mock_inject.return_value = {"contributors": [{"login": "user1"}]}
        mock_has_changes.return_value = True
        mock_create_pr.return_value = None

        # Execute workflow
        cli.main(
            organisation="test-org",
            target_repo="test-repo",
            github_token="test-token",
            target_filepath=".all-contributorsrc",
            base_branch="main",
            head_branch="test-branch",
            working_dir="/test/repo",
        )

        # Verify push happened before PR creation
        mock_push.assert_called_once_with("test-branch", "/test/repo")
        mock_create_pr.assert_called_once_with(
            "test-org", "test-repo", "main", "test-branch", False, None, "test-token"
        )
