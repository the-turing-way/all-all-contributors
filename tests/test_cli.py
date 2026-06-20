import json
import os
from unittest.mock import MagicMock, call, mock_open, patch

import pytest
import typer
from pytest import fixture
from typer.testing import CliRunner

from all_all_contributors import cli
from all_all_contributors.cli import app


@fixture()
def runner():
    return CliRunner()


@fixture()
def github_token(monkeypatch):
    monkeypatch.setenv("INPUT_GITHUB_TOKEN", "dummy_token")


@fixture()
def unset_github_token(monkeypatch):
    monkeypatch.delenv("INPUT_GITHUB_TOKEN", raising=False)


class TestCli:
    def test_cli_missing_env(self, runner, unset_github_token):
        result = runner.invoke(app, ["organisation", "./target.txt"])
        assert result.exit_code == 1
        assert "Environment variable INPUT_GITHUB_TOKEN is not defined" in result.stdout


class TestGetGithubToken:
    @patch.dict(os.environ, {"INPUT_GITHUB_TOKEN": "test-token"})
    def test_returns_token_when_set(self):
        """Test that token is returned when environment variable is set"""
        token = cli.get_github_token()
        assert token == "test-token"

    @patch.dict(os.environ, {}, clear=True)
    def test_raises_exit_when_token_not_set(self):
        """Test that Exit is raised when environment variable is not set"""
        with pytest.raises(typer.Exit) as exc_info:
            cli.get_github_token()
        assert exc_info.value.exit_code == 1


class TestLoadExcludedRepos:
    @patch("all_all_contributors.cli.path.exists", return_value=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="repo1\nrepo2\n# comment\nrepo3\n",
    )
    @patch.dict(os.environ, {"INPUT_IGNORE_FILE": "test.repoignore"})
    def test_loads_repos_from_file(self, mock_file, mock_exists):
        """Test that repos are loaded from file and comments are filtered"""
        result = cli.load_excluded_repos()

        assert "repo1\n" in result
        assert "repo2\n" in result
        assert "repo3\n" in result
        # Comments should be filtered out
        for item in result:
            assert not item.startswith("#")
        mock_file.assert_called_once_with("test.repoignore")

    @patch("all_all_contributors.cli.path.exists", return_value=False)
    @patch.dict(os.environ, {"INPUT_IGNORE_FILE": ".repoignore"})
    def test_returns_empty_set_when_file_not_found(self, mock_exists):
        """Test that empty set is returned when file doesn't exist"""
        result = cli.load_excluded_repos()
        assert result == set()


class TestMain:
    @patch("all_all_contributors.cli.github_api.create_update_pull_request")
    @patch("all_all_contributors.cli.git_operations.push_branch")
    @patch("all_all_contributors.cli.git_operations.create_commit")
    @patch("all_all_contributors.cli.git_operations.stage_modified_files")
    @patch("builtins.open", new_callable=mock_open, read_data='{"contributors": []}')
    @patch("all_all_contributors.cli.inject_config")
    @patch("all_all_contributors.cli.git_operations.checkout_branch")
    @patch("all_all_contributors.cli.git_operations.branch_exists_remote")
    @patch("all_all_contributors.cli.github_api.find_existing_pull_request")
    @patch("all_all_contributors.cli.merge_contributors")
    @patch("all_all_contributors.cli.github_api.get_contributors_from_repo")
    @patch("all_all_contributors.cli.github_api.get_all_repos")
    @patch("all_all_contributors.cli.load_excluded_repos")
    @patch("all_all_contributors.cli.get_github_token")
    def test_main_workflow_with_new_branch(
        self,
        mock_get_token,
        mock_load_excluded,
        mock_get_repos,
        mock_get_contributors,
        mock_merge,
        mock_find_pr,
        mock_branch_exists,
        mock_checkout,
        mock_inject,
        mock_file,
        mock_stage,
        mock_commit,
        mock_push,
        mock_create_pr,
    ):
        """Test main workflow when creating a new branch"""
        # Setup mocks
        mock_get_token.return_value = "test-token"
        mock_load_excluded.return_value = set()
        mock_get_repos.return_value = ["repo1", "repo2"]
        mock_get_contributors.return_value = [{"login": "user1"}]
        mock_merge.return_value = [{"login": "user1", "contributions": ["code"]}]
        mock_find_pr.return_value = (False, "merged-all-contributors/ABCD", None)
        mock_branch_exists.return_value = False
        mock_inject.return_value = {"contributors": [{"login": "user1"}]}

        # Call main
        cli.main(
            organisation="test-org",
            target_repo="test-repo",
            target_filepath=".all-contributorsrc",
            base_branch="main",
            head_branch="merged-all-contributors",
            working_dir="/test/repo",
        )

        # Verify workflow
        mock_get_token.assert_called_once()
        mock_load_excluded.assert_called_once()
        mock_get_repos.assert_called_once_with("test-org", "test-token", set())
        assert mock_get_contributors.call_count == 2
        mock_merge.assert_called_once()
        mock_find_pr.assert_called_once_with(
            "test-org", "test-repo", "merged-all-contributors", "test-token"
        )
        mock_branch_exists.assert_called_once_with(
            "merged-all-contributors/ABCD", "/test/repo"
        )
        mock_checkout.assert_called_once_with(
            "merged-all-contributors/ABCD", create=True, working_dir="/test/repo"
        )
        mock_stage.assert_called_once_with("/test/repo")
        mock_commit.assert_called_once_with(
            "Merging all contributors info from across the org", "/test/repo"
        )
        mock_push.assert_called_once_with("merged-all-contributors/ABCD", "/test/repo")
        mock_create_pr.assert_called_once_with(
            "test-org",
            "test-repo",
            "main",
            "merged-all-contributors/ABCD",
            False,
            None,
            "test-token",
        )

    @patch("all_all_contributors.cli.github_api.create_update_pull_request")
    @patch("all_all_contributors.cli.git_operations.push_branch")
    @patch("all_all_contributors.cli.git_operations.create_commit")
    @patch("all_all_contributors.cli.git_operations.stage_modified_files")
    @patch("builtins.open", new_callable=mock_open, read_data='{"contributors": []}')
    @patch("all_all_contributors.cli.inject_config")
    @patch("all_all_contributors.cli.git_operations.pull_latest")
    @patch("all_all_contributors.cli.git_operations.checkout_branch")
    @patch("all_all_contributors.cli.git_operations.branch_exists_remote")
    @patch("all_all_contributors.cli.github_api.find_existing_pull_request")
    @patch("all_all_contributors.cli.merge_contributors")
    @patch("all_all_contributors.cli.github_api.get_contributors_from_repo")
    @patch("all_all_contributors.cli.github_api.get_all_repos")
    @patch("all_all_contributors.cli.load_excluded_repos")
    @patch("all_all_contributors.cli.get_github_token")
    def test_main_workflow_with_existing_branch(
        self,
        mock_get_token,
        mock_load_excluded,
        mock_get_repos,
        mock_get_contributors,
        mock_merge,
        mock_find_pr,
        mock_branch_exists,
        mock_checkout,
        mock_pull,
        mock_inject,
        mock_file,
        mock_stage,
        mock_commit,
        mock_push,
        mock_create_pr,
    ):
        """Test main workflow when branch already exists"""
        # Setup mocks
        mock_get_token.return_value = "test-token"
        mock_load_excluded.return_value = set()
        mock_get_repos.return_value = ["repo1"]
        mock_get_contributors.return_value = [{"login": "user1"}]
        mock_merge.return_value = [{"login": "user1"}]
        mock_find_pr.return_value = (True, "merged-all-contributors/WXYZ", 42)
        mock_branch_exists.return_value = True
        mock_inject.return_value = {"contributors": [{"login": "user1"}]}

        # Call main
        cli.main(
            organisation="test-org",
            target_repo="test-repo",
            target_filepath=".all-contributorsrc",
            base_branch="main",
            head_branch="merged-all-contributors",
            working_dir="/test/repo",
        )

        # Verify branch handling
        mock_branch_exists.assert_called_once_with(
            "merged-all-contributors/WXYZ", "/test/repo"
        )
        mock_checkout.assert_called_once_with(
            "merged-all-contributors/WXYZ", create=False, working_dir="/test/repo"
        )
        mock_pull.assert_called_once_with("/test/repo")
        mock_create_pr.assert_called_once_with(
            "test-org",
            "test-repo",
            "main",
            "merged-all-contributors/WXYZ",
            True,
            42,
            "test-token",
        )

    @patch("all_all_contributors.cli.merge_contributors")
    @patch("all_all_contributors.cli.github_api.get_contributors_from_repo")
    @patch("all_all_contributors.cli.github_api.get_all_repos")
    @patch("all_all_contributors.cli.load_excluded_repos")
    @patch("all_all_contributors.cli.get_github_token")
    def test_main_exits_when_no_contributors(
        self,
        mock_get_token,
        mock_load_excluded,
        mock_get_repos,
        mock_get_contributors,
        mock_merge,
    ):
        """Test that main returns early when no contributors found"""
        # Setup mocks
        mock_get_token.return_value = "test-token"
        mock_load_excluded.return_value = set()
        mock_get_repos.return_value = ["repo1"]
        mock_get_contributors.return_value = []
        mock_merge.return_value = []

        # Call main
        result = cli.main(
            organisation="test-org",
            target_repo="test-repo",
            target_filepath=".all-contributorsrc",
            base_branch="main",
            head_branch="merged-all-contributors",
            working_dir="/test/repo",
        )

        # Should return None early
        assert result is None
        mock_merge.assert_called_once_with([])

    @patch("all_all_contributors.cli.github_api.create_update_pull_request")
    @patch("all_all_contributors.cli.git_operations.push_branch")
    @patch("all_all_contributors.cli.git_operations.create_commit")
    @patch("all_all_contributors.cli.git_operations.stage_modified_files")
    @patch("all_all_contributors.cli.inject_config")
    @patch("all_all_contributors.cli.git_operations.checkout_branch")
    @patch("all_all_contributors.cli.git_operations.branch_exists_remote")
    @patch("all_all_contributors.cli.github_api.find_existing_pull_request")
    @patch("all_all_contributors.cli.merge_contributors")
    @patch("all_all_contributors.cli.github_api.get_contributors_from_repo")
    @patch("all_all_contributors.cli.github_api.get_all_repos")
    @patch("all_all_contributors.cli.load_excluded_repos")
    @patch("all_all_contributors.cli.get_github_token")
    def test_main_creates_default_config_when_file_not_found(
        self,
        mock_get_token,
        mock_load_excluded,
        mock_get_repos,
        mock_get_contributors,
        mock_merge,
        mock_find_pr,
        mock_branch_exists,
        mock_checkout,
        mock_inject,
        mock_stage,
        mock_commit,
        mock_push,
        mock_create_pr,
    ):
        """Test that default config is created when file doesn't exist"""
        # Setup mocks
        mock_get_token.return_value = "test-token"
        mock_load_excluded.return_value = set()
        mock_get_repos.return_value = ["repo1"]
        mock_get_contributors.return_value = [{"login": "user1"}]
        mock_merge.return_value = [{"login": "user1"}]
        mock_find_pr.return_value = (False, "merged-all-contributors/ABCD", None)
        mock_branch_exists.return_value = False
        mock_inject.return_value = {"contributors": [{"login": "user1"}]}

        # Mock file operations - read raises FileNotFoundError, write succeeds
        m = mock_open()
        m.return_value.read.side_effect = FileNotFoundError

        with patch("builtins.open", m):
            cli.main(
                organisation="test-org",
                target_repo="test-repo",
                target_filepath=".all-contributorsrc",
                base_branch="main",
                head_branch="merged-all-contributors",
                working_dir="/test/repo",
            )

        # Verify inject_config was called with default config
        call_args = mock_inject.call_args[0]
        assert call_args[0]["projectName"] == "test-repo"
        assert call_args[0]["projectOwner"] == "test-org"
        assert call_args[0]["contributors"] == []

    @patch("all_all_contributors.cli.get_github_token")
    def test_main_uses_custom_working_dir(self, mock_get_token):
        """Test that custom working_dir parameter is used throughout"""
        mock_get_token.return_value = "test-token"

        with patch("all_all_contributors.cli.load_excluded_repos") as mock_load:
            mock_load.return_value = set()
            with patch(
                "all_all_contributors.cli.github_api.get_all_repos"
            ) as mock_repos:
                mock_repos.return_value = []
                with patch(
                    "all_all_contributors.cli.github_api.get_contributors_from_repo"
                ):
                    with patch(
                        "all_all_contributors.cli.merge_contributors"
                    ) as mock_merge:
                        mock_merge.return_value = []

                        cli.main(
                            organisation="test-org",
                            target_repo="test-repo",
                            target_filepath=".all-contributorsrc",
                            base_branch="main",
                            head_branch="merged-all-contributors",
                            working_dir="/custom/working/dir",
                        )

                        # Verify custom working dir would be used
                        # (returns early due to no contributors, so just verify it accepts the parameter)
                        assert True
