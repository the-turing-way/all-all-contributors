import random
import string
from unittest.mock import MagicMock, patch

import pytest
import requests

from all_all_contributors import github_api


class TestGetHeaders:
    def test_returns_correct_headers(self):
        """Test that headers include correct accept and auth"""
        token = "test-token"

        headers = github_api._get_headers(token)

        assert headers["Accept"] == "application/vnd.github.v3+json"
        assert headers["Authorization"] == "token test-token"


class TestGetAllRepos:
    @patch("all_all_contributors.github_api.get_request")
    def test_fetches_repos_and_filters_excluded(self, mock_get):
        """Test that repos are fetched and excluded repos are filtered"""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "excluded-repo"},
            {"name": "repo3"},
        ]
        mock_response.headers = {}  # No pagination
        mock_get.return_value = mock_response

        result = github_api.get_all_repos("test-org", "test-token", {"excluded-repo"})

        assert result == ["repo1", "repo2", "repo3"]
        mock_get.assert_called_once_with(
            "https://api.github.com/orgs/test-org/repos",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token test-token",
            },
            params={"type": "public", "per_page": 100},
        )

    @patch("all_all_contributors.github_api.get_request")
    def test_handles_pagination(self, mock_get):
        """Test that pagination is handled correctly"""
        # First page response
        mock_response1 = MagicMock()
        mock_response1.json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"},
        ]
        mock_response1.headers = {"link": "next_url"}
        mock_response1.links = {"next": {"url": "next_url"}}

        # Second page response
        mock_response2 = MagicMock()
        mock_response2.json.return_value = [
            {"name": "repo3"},
            {"name": "repo4"},
        ]
        mock_response2.headers = {}  # No more pages

        mock_get.side_effect = [mock_response1, mock_response2]

        result = github_api.get_all_repos("test-org", "test-token", set())

        assert result == ["repo1", "repo2", "repo3", "repo4"]
        assert mock_get.call_count == 2


class TestGetContributorsFromRepo:
    @patch("all_all_contributors.github_api.get_request")
    def test_fetches_contributors_successfully(self, mock_get):
        """Test that contributors are fetched from repo"""
        # First call returns file metadata with download_url
        mock_response1 = {
            "download_url": "https://raw.githubusercontent.com/test-org/repo/.all-contributorsrc"
        }
        # Second call returns actual file contents
        mock_response2 = {
            "contributors": [
                {"login": "user1", "contributions": ["code"]},
                {"login": "user2", "contributions": ["doc"]},
            ]
        }
        mock_get.side_effect = [mock_response1, mock_response2]

        result = github_api.get_contributors_from_repo(
            "test-org", "test-repo", "test-token"
        )

        assert len(result) == 2
        assert result[0]["login"] == "user1"
        assert result[1]["login"] == "user2"
        assert mock_get.call_count == 2

    @patch("all_all_contributors.github_api.get_request")
    def test_returns_empty_list_on_404(self, mock_get):
        """Test that 404 errors return empty list"""
        mock_get.side_effect = requests.HTTPError("404 Client Error")

        result = github_api.get_contributors_from_repo(
            "test-org", "test-repo", "test-token"
        )

        assert result == []

    @patch("all_all_contributors.github_api.get_request")
    def test_raises_on_other_http_errors(self, mock_get):
        """Test that non-404 HTTP errors are raised"""
        mock_get.side_effect = requests.HTTPError("500 Server Error")

        with pytest.raises(requests.HTTPError):
            github_api.get_contributors_from_repo("test-org", "test-repo", "test-token")

    @patch("all_all_contributors.github_api.get_request")
    def test_uses_custom_filepath(self, mock_get):
        """Test that custom filepath is used in API call"""
        mock_response1 = {"download_url": "https://example.com/custom.json"}
        mock_response2 = {"contributors": []}
        mock_get.side_effect = [mock_response1, mock_response2]

        github_api.get_contributors_from_repo(
            "test-org", "test-repo", "test-token", filepath="custom.json"
        )

        # First call should use custom filepath
        first_call_url = mock_get.call_args_list[0][0][0]
        assert first_call_url.endswith("/custom.json")


class TestFetchAllContributors:
    @patch("all_all_contributors.github_api.get_contributors_from_repo")
    def test_fetches_contributors_from_multiple_repos(self, mock_get_contributors):
        """Test that contributors are fetched from all repos and combined"""
        mock_get_contributors.side_effect = [
            [{"login": "user1", "contributions": ["code"]}],
            [{"login": "user2", "contributions": ["doc"]}],
            [{"login": "user3", "contributions": ["test"]}],
        ]
        repos = ["repo1", "repo2", "repo3"]

        result = github_api.fetch_all_contributors("test-org", "test-token", repos)

        assert len(result) == 3
        assert result[0]["login"] == "user1"
        assert result[1]["login"] == "user2"
        assert result[2]["login"] == "user3"
        assert mock_get_contributors.call_count == 3

    @patch("all_all_contributors.github_api.get_contributors_from_repo")
    def test_returns_empty_list_when_no_repos(self, mock_get_contributors):
        """Test that empty list is returned when no repos provided"""
        result = github_api.fetch_all_contributors("test-org", "test-token", [])

        assert result == []
        mock_get_contributors.assert_not_called()

    @patch("all_all_contributors.github_api.get_contributors_from_repo")
    def test_handles_repos_with_no_contributors(self, mock_get_contributors):
        """Test that repos with no contributors don't break the flow"""
        mock_get_contributors.side_effect = [
            [{"login": "user1"}],
            [],  # No contributors
            [{"login": "user2"}],
        ]
        repos = ["repo1", "repo2", "repo3"]

        result = github_api.fetch_all_contributors("test-org", "test-token", repos)

        assert len(result) == 2
        assert result[0]["login"] == "user1"
        assert result[1]["login"] == "user2"


class TestFindExistingPullRequest:
    @patch("all_all_contributors.github_api.get_request")
    def test_returns_false_when_no_pr_exists(self, mock_get):
        """Test that function returns False and new branch name when no PR exists"""
        mock_get.return_value = [
            {"head": {"label": "test-org:some-other-branch"}, "number": 1}
        ]

        with patch.object(random, "sample", return_value=list("ABCD")):
            pr_exists, actual_head_branch, pr_number = (
                github_api.find_existing_pull_request(
                    "test-org", "test-repo", "merge-all-contributors", "test-token"
                )
            )

        assert pr_exists is False
        assert actual_head_branch == "merge-all-contributors/ABCD"
        assert pr_number is None
        mock_get.assert_called_once_with(
            "https://api.github.com/repos/test-org/test-repo/pulls",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token test-token",
            },
            params={"state": "open", "sort": "created", "direction": "desc"},
            output="json",
        )

    @patch("all_all_contributors.github_api.get_request")
    def test_returns_true_when_pr_exists(self, mock_get):
        """Test that function returns True and existing branch details when PR exists"""
        mock_get.return_value = [
            {"head": {"label": "test-org:merge-all-contributors/WXYZ"}, "number": 42}
        ]

        pr_exists, actual_head_branch, pr_number = (
            github_api.find_existing_pull_request(
                "test-org", "test-repo", "merge-all-contributors", "test-token"
            )
        )

        assert pr_exists is True
        assert actual_head_branch == "merge-all-contributors/WXYZ"
        assert pr_number == 42

    @patch("all_all_contributors.github_api.get_request")
    def test_matches_partial_branch_name(self, mock_get):
        """Test that branch name matching works with partial match"""
        mock_get.return_value = [
            {"head": {"label": "other-org:different-branch"}, "number": 1},
            {"head": {"label": "test-org:merge-all-contributors/TEST"}, "number": 10},
        ]

        pr_exists, actual_head_branch, pr_number = (
            github_api.find_existing_pull_request(
                "test-org", "test-repo", "merge-all-contributors", "test-token"
            )
        )

        assert pr_exists is True
        assert actual_head_branch == "merge-all-contributors/TEST"
        assert pr_number == 10


class TestCreateUpdatePullRequest:
    @patch("all_all_contributors.github_api.post_request")
    def test_creates_new_pull_request(self, mock_post):
        """Test that new PR is created when pr_exists is False"""
        mock_post.return_value = {"number": 123}

        github_api.create_update_pull_request(
            "test-org",
            "test-repo",
            "main",
            "merge-all-contributors/ABCD",
            pr_exists=False,
            pr_number=None,
            github_token="test-token",
        )

        mock_post.assert_called_once_with(
            "https://api.github.com/repos/test-org/test-repo/pulls",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token test-token",
            },
            json={
                "title": "Merging all-contributors across the org",
                "body": "",
                "base": "main",
                "head": "merge-all-contributors/ABCD",
            },
            return_json=True,
        )

    @patch("all_all_contributors.github_api.patch_request")
    def test_updates_existing_pull_request(self, mock_patch):
        """Test that existing PR is updated when pr_exists is True"""
        mock_patch.return_value = {"number": 42}

        github_api.create_update_pull_request(
            "test-org",
            "test-repo",
            "main",
            "merge-all-contributors/WXYZ",
            pr_exists=True,
            pr_number=42,
            github_token="test-token",
        )

        mock_patch.assert_called_once_with(
            "https://api.github.com/repos/test-org/test-repo/pulls/42",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token test-token",
            },
            json={
                "title": "Merging all-contributors across the org",
                "body": "",
                "base": "main",
                "state": "open",
            },
            return_json=True,
        )
