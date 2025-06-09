import base64
import unittest
from unittest.mock import call, patch

from all_all_contributors.github_api import GitHubAPI
from all_all_contributors.yaml_parser import YamlParser

yaml = YamlParser()


class TestGitHubAPI(unittest.TestCase):
    def test_create_commit(self):
        github = GitHubAPI(
            "octocat",
            "octocat",
            "ThIs_Is_A_t0k3n",
            ".all-contributorsrc",
        )

        github.sha = "test_sha"
        commit_msg = "This is a commit message"
        contents = {"key1": "This is a test"}

        contents = yaml.object_to_yaml_str(contents).encode("utf-8")
        contents = base64.b64encode(contents)
        contents = contents.decode("utf-8")

        body = {
            "message": commit_msg,
            "content": contents,
            "sha": github.sha,
            "branch": github.head_branch,
        }

        with patch("all_all_contributors.github_api.put") as mock:
            github.create_commit(
                contents,
                commit_msg=commit_msg,
            )

            self.assertEqual(mock.call_count, 1)
            mock.assert_called_with(
                "/".join(
                    [
                        github.api_url,
                        "repos",
                        github.target_repo_name,
                        "contents",
                        github.target_filepath,
                    ]
                ),
                json=body,
                headers=github.headers,
            )

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
                "/".join([github.api_url, "repos", github.target_repo_name, "pulls"]),
                headers=github.headers,
                json=expected_pr,
                return_json=True,
            )

    def test_create_ref(self):
        github = GitHubAPI(
            "octocat",
            "octocat",
            "ThIs_Is_A_t0k3n",
            ".all-contributorsrc",
        )
        test_ref = "test_ref"
        test_sha = "test_sha"

        test_body = {"ref": f"refs/heads/{test_ref}", "sha": test_sha}

        with patch("all_all_contributors.github_api.post_request") as mock:
            github.create_ref(test_ref, test_sha)

            self.assertEqual(mock.call_count, 1)
            mock.assert_called_with(
                "/".join(
                    [github.api_url, "repos", github.target_repo_name, "git", "refs"]
                ),
                headers=github.headers,
                json=test_body,
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
                "/".join([github.api_url, "repos", github.target_repo_name, "pulls"]),
                headers=github.headers,
                params={"state": "open", "sort": "created", "direction": "desc"},
                output="json",
            )
            self.assertFalse(github.pr_exists)
            self.assertTrue(github.head_branch.startswith("merge-all-contributors"))

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
                        "label": "merge-all-contributors",
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
                "/".join([github.api_url, "repos", github.target_repo_name, "pulls"]),
                headers=github.headers,
                params={"state": "open", "sort": "created", "direction": "desc"},
                output="json",
            )
            self.assertTrue(github.pr_exists)
            self.assertEqual(github.head_branch, "merge-all-contributors")
            self.assertEqual(github.pr_number, 1)

    def test_get_ref(self):
        github = GitHubAPI(
            "octocat",
            "octocat",
            "ThIs_Is_A_t0k3n",
            ".all-contributorsrc",
        )
        test_ref = "test_ref"

        mock_get = patch(
            "all_all_contributors.github_api.get_request",
            return_value={"object": {"sha": "sha"}},
        )

        with mock_get as mock:
            resp = github.get_ref(test_ref)

            self.assertEqual(mock.call_count, 1)
            mock.assert_called_with(
                "/".join(
                    [
                        github.api_url,
                        "repos",
                        github.target_repo_name,
                        "git",
                        "ref",
                        "heads",
                        test_ref,
                    ]
                ),
                headers=github.headers,
                output="json",
            )
            self.assertDictEqual(resp, {"object": {"sha": "sha"}})

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
