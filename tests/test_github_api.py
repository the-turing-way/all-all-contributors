import unittest
from unittest.mock import patch

from all_all_contributors.github_api import GitHubAPI


class TestGitHubAPI(unittest.TestCase):
    def test_create_update_pull_request(self):
        github = GitHubAPI(
            "octocat",
            "octocat",
            "ThIs_Is_A_t0k3n",
            ".all-contributorsrc",
        )
        github.pr_exists = False

        expected_pr = {
            "title": "Merging all-contributors across the org",
            "body": "",
            "base": github.base_branch,
            "head": github.head_branch,
        }

        with patch("all_all_contributors.github_api.post_request") as mock:
            github.create_update_pull_request()

            self.assertEqual(mock.call_count, 1)
            mock.assert_called_with(
                "/".join(
                    [
                        github.api_url,
                        "repos",
                        github.org_name,
                        github.target_repo_name,
                        "pulls",
                    ]
                ),
                headers=github.headers,
                json=expected_pr,
                return_json=True,
            )

    def test_find_existing_pull_request_no_matches(self):
        github = GitHubAPI(
            "octocat",
            "octocat",
            "ThIs_Is_A_t0k3n",
            ".all-contributorsrc",
        )

        mock_get = patch(
            "all_all_contributors.github_api.get_request",
            return_value=[
                {
                    "head": {
                        "label": "some_branch",
                    }
                }
            ],
        )

        with mock_get as mock:
            github.find_existing_pull_request()

            self.assertEqual(mock.call_count, 1)
            mock.assert_called_with(
                "/".join(
                    [
                        github.api_url,
                        "repos",
                        github.org_name,
                        github.target_repo_name,
                        "pulls",
                    ]
                ),
                headers=github.headers,
                params={"state": "open", "sort": "created", "direction": "desc"},
                output="json",
            )
            self.assertFalse(github.pr_exists)
            self.assertTrue(github.head_branch.startswith("merged-all-contributors"))

    def test_find_existing_pull_request_match(self):
        github = GitHubAPI(
            "octocat",
            "octocat",
            "ThIs_Is_A_t0k3n",
            ".all-contributorsrc",
        )

        mock_get = patch(
            "all_all_contributors.github_api.get_request",
            return_value=[
                {
                    "head": {
                        "label": "merged-all-contributors",
                    },
                    "number": 1,
                }
            ],
        )

        with mock_get as mock:
            github.find_existing_pull_request()
            print(github.head_branch)
            print(github.pr_exists)

            self.assertEqual(mock.call_count, 1)
            mock.assert_called_with(
                "/".join(
                    [
                        github.api_url,
                        "repos",
                        github.org_name,
                        github.target_repo_name,
                        "pulls",
                    ]
                ),
                headers=github.headers,
                params={"state": "open", "sort": "created", "direction": "desc"},
                output="json",
            )
            self.assertTrue(github.pr_exists)
            self.assertEqual(github.head_branch, "merged-all-contributors")
            self.assertEqual(github.pr_number, 1)

    def test_update_existing_pr(self):
        github = GitHubAPI(
            "octocat",
            "octocat",
            "ThIs_Is_A_t0k3n",
            ".all-contributorsrc",
        )
        github.pr_exists = True
        github.pr_number = 1

        expected_pr = {
            "title": "Merging all-contributors across the org",
            "body": "",
            "base": github.base_branch,
            "state": "open",
        }

        mock_patch = patch(
            "all_all_contributors.github_api.patch_request", return_value={"number": 1}
        )

        with mock_patch as mock:
            github.create_update_pull_request()

            mock.assert_called_with(
                "/".join(
                    [
                        github.api_url,
                        "repos",
                        github.org_name,
                        github.target_repo_name,
                        "pulls",
                        str(github.pr_number),
                    ]
                ),
                headers=github.headers,
                json=expected_pr,
                return_json=True,
            )
            self.assertDictEqual(mock.return_value, {"number": 1})


if __name__ == "__main__":
    unittest.main()
