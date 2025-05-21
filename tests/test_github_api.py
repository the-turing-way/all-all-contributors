
import base64
import unittest
from unittest.mock import call, patch

from all_all_contributors.github_api import GitHubAPI
from all_all_contributors.yaml_parser import YamlParser

yaml = YamlParser()


class TestInputs():
    def __init__(
        self,
        repository,
        github_token,
        filepath,
        base_branch="main",
        head_branch="merge-all-contributors",
        ignore_file=".repoignore",
    ):
        self.repository = repository
        self.github_token = github_token
        self.filepath = filepath
        self.base_branch = base_branch
        self.head_branch = head_branch
        self.ignore_file = ignore_file

        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {github_token}",
        }


class TestGitHubAPI(unittest.TestCase):
    def test_create_commit(self):
        inputs = TestInputs(
            "octocat/octocat",
            "ThIs_Is_A_t0k3n",
            ".all-contributorsrc",
        )
        github = GitHubAPI(inputs)

        inputs.sha = "test_sha"
        commit_msg = "This is a commit message"
        contents = {"key1": "This is a test"}

        contents = yaml.object_to_yaml_str(contents).encode("utf-8")
        contents = base64.b64encode(contents)
        contents = contents.decode("utf-8")

        body = {
            "message": commit_msg,
            "content": contents,
            "sha": inputs.sha,
            "branch": inputs.head_branch,
        }

        with patch("all_all_contributors.github_api.put") as mock:
            github.create_commit(
                commit_msg,
                contents,
            )

            self.assertEqual(mock.call_count, 1)
            mock.assert_called_with(
                "/".join([github.api_url, "contents", inputs.filepath]),
                json=body,
                headers=inputs.headers,
            )

    def test_create_update_pull_request(self):
        inputs = TestInputs(
            "octocat/octocat",
            "ThIs_Is_A_t0k3n",
            ".all-contributorsrc",
        )
        github = GitHubAPI(inputs)
        github.pr_exists = False

        expected_pr = {
            "title": "Merging all-contributors across the org",
            "body": "",
            "base": inputs.base_branch,
            "head": inputs.head_branch,
        }

        with patch("all_all_contributors.github_api.post_request") as mock:
            github.create_update_pull_request()

            self.assertEqual(mock.call_count, 1)
            mock.assert_called_with(
                "/".join([github.api_url, "pulls"]),
                headers=inputs.headers,
                json=expected_pr,
                return_json=True,
            )

    def test_create_ref(self):
        inputs = TestInputs(
            "octocat/octocat",
            "ThIs_Is_A_t0k3n",
            ".all-contributorsrc",
        )
        github = GitHubAPI(inputs)
        test_ref = "test_ref"
        test_sha = "test_sha"

        test_body = {"ref": f"refs/heads/{test_ref}", "sha": test_sha}

        with patch("all_all_contributors.github_api.post_request") as mock:
            github.create_ref(test_ref, test_sha)

            self.assertEqual(mock.call_count, 1)
            mock.assert_called_with(
                "/".join([github.api_url, "git", "refs"]),
                headers=inputs.headers,
                json=test_body,
            )

    def test_find_existing_pull_request_no_matches(self):
        inputs = TestInputs(
            "octocat/octocat",
            "ThIs_Is_A_t0k3n",
            ".all-contributorsrc",
        )
        github = GitHubAPI(inputs)

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
                "/".join([github.api_url, "pulls"]),
                headers=inputs.headers,
                params={"state": "open", "sort": "created", "direction": "desc"},
                output="json",
            )
            self.assertFalse(github.pr_exists)
            self.assertTrue(
                inputs.head_branch.startswith("merge-all-contributors")
            )

    def test_find_existing_pull_request_match(self):
        inputs = TestInputs(
            "octocat/octocat",
            "ThIs_Is_A_t0k3n",
            ".all-contributorsrc",
        )
        github = GitHubAPI(inputs)

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

            self.assertEqual(mock.call_count, 1)
            mock.assert_called_with(
                "/".join([github.api_url, "pulls"]),
                headers=inputs.headers,
                params={"state": "open", "sort": "created", "direction": "desc"},
                output="json",
            )
            self.assertTrue(github.pr_exists)
            self.assertEqual(
                inputs.head_branch, "merge-all-contributors"
            )
            self.assertEqual(github.pr_number, 1)

    def test_get_ref(self):
        inputs = TestInputs(
            "octocat/octocat",
            "ThIs_Is_A_t0k3n",
            ".all-contributorsrc",
        )
        github = GitHubAPI(inputs)
        test_ref = "test_ref"

        mock_get = patch(
            "all_all_contributors.github_api.get_request", return_value={"object": {"sha": "sha"}}
        )

        with mock_get as mock:
            resp = github.get_ref(test_ref)

            self.assertEqual(mock.call_count, 1)
            mock.assert_called_with(
                "/".join([github.api_url, "git", "ref", "heads", test_ref]),
                headers=inputs.headers,
                output="json",
            )
            self.assertDictEqual(resp, {"object": {"sha": "sha"}})

    def test_update_existing_pr(self):
        inputs = TestInputs(
            "octocat/octocat",
            "ThIs_Is_A_t0k3n",
            ".all-contributorsrc",
        )
        github = GitHubAPI(inputs)
        github.pr_exists = True
        github.pr_number = 1

        expected_pr = {
            "title": "Merging all-contributors across the org",
            "body": "",
            "base": inputs.base_branch,
            "state": "open",
        }

        mock_patch = patch(
            "all_all_contributors.github_api.patch_request", return_value={"number": 1}
        )

        with mock_patch as mock:
            github.create_update_pull_request()

            mock.assert_called_with(
                "/".join([github.api_url, "pulls", str(github.pr_number)]),
                headers=inputs.headers,
                json=expected_pr,
                return_json=True,
            )
            self.assertDictEqual(mock.return_value, {"number": 1})


if __name__ == "__main__":
    unittest.main()
