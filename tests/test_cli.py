from unittest.mock import MagicMock, patch

from all_all_contributors.cli import app


class TestCli:
    def test_cli_missing_env(self, runner, unset_github_token):
        result = runner.invoke(app, ["organisation", "./target.txt"])
        assert result.exit_code == 1
        assert "Environment variable INPUT_GITHUB_TOKEN is not defined" in result.stdout

    @patch("all_all_contributors.cli.run_all_contributors_generate")
    @patch("all_all_contributors.cli.verify_all_contributors_environment")
    @patch("all_all_contributors.cli.GitCLI")
    @patch("all_all_contributors.cli.GitHubAPI")
    @patch("all_all_contributors.cli.read_contributors_file")
    def test_cli_happy_path(
        self,
        mock_read_contributors,
        mock_github_api_cls,
        mock_git_cli_cls,
        mock_verify_env,
        mock_run_generate,
        runner,
        github_token,
        tmp_path,
    ):
        """Happy path: list repos → collect contributors → merge → commit → push → PR"""
        # Set up GitCLI mock
        mock_git = MagicMock()
        mock_git_cli_cls.return_value = mock_git
        mock_git.check_for_changes.return_value = True

        # Set up GitHubAPI mock
        mock_api = MagicMock()
        mock_github_api_cls.return_value = mock_api
        mock_api.find_existing_pull_request.return_value = (
            False,
            "merged-all-contributors/abcd",
        )
        mock_api.head_branch = "merged-all-contributors/abcd"
        mock_api.get_all_repos.return_value = ["repo-a", "repo-b"]
        mock_api.get_contributors_from_repo.side_effect = [
            [
                {
                    "login": "user1",
                    "name": "User One",
                    "avatar_url": "u",
                    "profile": "p",
                    "contributions": ["code"],
                }
            ],
            [
                {
                    "login": "user2",
                    "name": "User Two",
                    "avatar_url": "u",
                    "profile": "p",
                    "contributions": ["doc"],
                }
            ],
        ]

        # Local contributors file read
        mock_read_contributors.side_effect = [
            # First call: read contributors list
            [
                {
                    "login": "user3",
                    "name": "User Three",
                    "avatar_url": "u",
                    "profile": "p",
                    "contributions": ["infra"],
                }
            ],
            # Second call: read full file (full_file=True)
            {
                "files": ["README.md"],
                "contributors": [
                    {
                        "login": "user3",
                        "name": "User Three",
                        "avatar_url": "u",
                        "profile": "p",
                        "contributions": ["infra"],
                    }
                ],
                "projectName": "test",
                "projectOwner": "org",
            },
        ]

        result = runner.invoke(
            app,
            [
                "my-org",
                "target-repo",
                ".all-contributorsrc",
                "main",
                "merged-all-contributors",
                "--repo-dir",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0, f"CLI failed: {result.output}"

        # Verify GitCLI orchestration
        mock_git.verify_environment.assert_called_once()
        mock_git.create_branch.assert_called_once_with(
            "merged-all-contributors/abcd", "main"
        )
        mock_git.commit_file.assert_called_once_with(".all-contributorsrc")
        mock_git.push_branch.assert_called_once_with("merged-all-contributors/abcd")

        # Verify GitHub API orchestration
        mock_api.find_existing_pull_request.assert_called_once()
        mock_api.get_all_repos.assert_called_once()
        mock_api.create_update_pull_request.assert_called_once()

    @patch("all_all_contributors.cli.verify_all_contributors_environment")
    @patch("all_all_contributors.cli.GitCLI")
    @patch("all_all_contributors.cli.GitHubAPI")
    @patch("all_all_contributors.cli.read_contributors_file")
    def test_cli_no_contributors_skips_commit(
        self,
        mock_read_contributors,
        mock_github_api_cls,
        mock_git_cli_cls,
        mock_verify_env,
        runner,
        github_token,
    ):
        """Req 8.7: no contributors → skip commit/push/PR, exit 0"""
        mock_git = MagicMock()
        mock_git_cli_cls.return_value = mock_git

        mock_api = MagicMock()
        mock_github_api_cls.return_value = mock_api
        mock_api.find_existing_pull_request.return_value = (
            False,
            "merged-all-contributors/abcd",
        )
        mock_api.head_branch = "merged-all-contributors/abcd"
        mock_api.get_all_repos.return_value = []
        mock_api.get_contributors_from_repo.return_value = []

        mock_read_contributors.return_value = []

        result = runner.invoke(
            app,
            [
                "my-org",
                "target-repo",
                ".all-contributorsrc",
                "main",
                "merged-all-contributors",
            ],
        )

        assert result.exit_code == 0
        mock_git.commit_file.assert_not_called()
        mock_git.push_branch.assert_not_called()
        mock_api.create_update_pull_request.assert_not_called()

    @patch("all_all_contributors.cli.GitCLI")
    @patch("all_all_contributors.cli.GitHubAPI")
    @patch("all_all_contributors.cli.read_contributors_file")
    def test_cli_git_error_exits_nonzero(
        self,
        mock_read_contributors,
        mock_github_api_cls,
        mock_git_cli_cls,
        runner,
        github_token,
    ):
        """Req 8.5: GitCLI fatal error → non-zero exit"""
        from all_all_contributors.external_cli import ExternalCLIError

        mock_git = MagicMock()
        mock_git_cli_cls.return_value = mock_git
        mock_git.create_branch.side_effect = ExternalCLIError(
            "git switch -c branch main", "fatal: not a git repository"
        )

        mock_api = MagicMock()
        mock_github_api_cls.return_value = mock_api
        mock_api.find_existing_pull_request.return_value = (
            False,
            "merged-all-contributors/abcd",
        )
        mock_api.head_branch = "merged-all-contributors/abcd"

        result = runner.invoke(
            app,
            [
                "my-org",
                "target-repo",
                ".all-contributorsrc",
                "main",
                "merged-all-contributors",
            ],
        )

        assert result.exit_code == 1

    @patch("all_all_contributors.cli.GitCLI")
    @patch("all_all_contributors.cli.GitHubAPI")
    @patch("all_all_contributors.cli.read_contributors_file")
    def test_cli_api_error_exits_nonzero(
        self,
        mock_read_contributors,
        mock_github_api_cls,
        mock_git_cli_cls,
        runner,
        github_token,
    ):
        """Req 8.6: GitHub API fatal error → non-zero exit"""
        import requests

        mock_git = MagicMock()
        mock_git_cli_cls.return_value = mock_git

        mock_api = MagicMock()
        mock_github_api_cls.return_value = mock_api
        mock_api.find_existing_pull_request.return_value = (
            False,
            "merged-all-contributors/abcd",
        )
        mock_api.head_branch = "merged-all-contributors/abcd"

        resp = requests.models.Response()
        resp.status_code = 500
        mock_api.get_all_repos.side_effect = requests.HTTPError(response=resp)

        result = runner.invoke(
            app,
            [
                "my-org",
                "target-repo",
                ".all-contributorsrc",
                "main",
                "merged-all-contributors",
            ],
        )

        assert result.exit_code == 1
