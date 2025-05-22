import os
import base64
import json
import random
import string
import jmespath
from requests import put
from .http_requests import get_request, patch_request, post_request
from .cli import load_excluded_repos


class GitHubAPI:
    """Interact with the GitHub API and perform various git-flow tasks"""

    def __init__(self,
        org_name: str,
        target_repo_name: str,
        github_token: str,
        target_filepath: str = ".all-contributorsrc",
        base_branch: str = "main",
        head_branch: str = "all-all-contributors",
    ):
        """
        Args:
            org_name (str): The name of the GitHub organisation to target
            target_repo_name (str): The name of the repo within `org_name` that
                will host the combined .all-contributorsrc file
            github_token (str): A GitHub token to authenticate API calls
            target_filepath (str, optional): The filepath within `target_repo_name`
                to the combined `.all-contributorsrc` file.
                (default: ".all-contributorsrc")
            base_branch (str, optional): The name of the default branch in
                `target_repo_name`. (default: "main")
            head_branch (str, optional): A prefix for branches created in
                `target_repo_name` for pull requests.
                (default: "all-all-contributors")
        """
        self.org_name = org_name
        self.target_repo_name = target_repo_name
        self.target_filepath = target_filepath
        self.base_branch = base_branch
        self.head_branch = head_branch

        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {github_token}",
        }

        self.api_url = "https://api.github.com"

    def create_commit(self, commit_msg, contents):
        """Create a commit over the GitHub API by creating or updating a file

        Args:
            commit_msg (str): A message describing the changes the commit applies
            contents (str): The content of the file to be updated, encoded in base64
        """
        print("Committing changes to file: {}", self.target_filepath)
        url = "/".join([self.api_url, "repos", self.target_repo_name, "contents", self.target_filepath])
        body = {
            "message": commit_msg,
            "content": contents,
            "sha": self.sha,
            "branch": self.head_branch,
        }
        put(url, json=body, headers=self.headers)

    def create_ref(self, ref, sha):
        """Create a new git reference (specifically, a branch) with GitHub's git
        database API endpoint

        Args:
            ref (str): The reference or branch name to create
            sha (str): The SHA of the parent commit to point the new reference to
        """
        print("Creating new branch: {}", ref)
        url = "/".join([self.api_url, "git", "refs"])
        body = {
            "ref": f"refs/heads/{ref}",
            "sha": sha,
        }
        post_request(url, headers=self.headers, json=body)

    def create_update_pull_request(self):
        """Create or update a Pull Request via the GitHub API"""
        url = "/".join([self.api_url, "pulls"])
        pr = {
            "title": "Merging all-contributors across the org",
            "body": "",  # FIXME: Add a descriptove PR body here
            "base": self.base_branch,
        }

        if self.pr_exists:
            print("Updating Pull Request...")

            url = "/".join([url, str(self.pr_number)])
            pr["state"] = "open"
            resp = patch_request(
                url,
                headers=self.headers,
                json=pr,
                return_json=True,
            )

            print(f"Pull Request #{resp['number']} updated!")
        else:
            print("Creating Pull Request...")

            pr["head"] = self.head_branch
            resp = post_request(
                url,
                headers=self.headers,
                json=pr,
                return_json=True,
            )

            print(f"Pull Request #{resp['number']} created!")

    def find_existing_pull_request(self):
        """Check if the bot already has an open Pull Request"""
        print(
            "Finding Pull Requests previously opened to merge all contributors files"
        )

        url = "/".join([self.api_url, "pulls"])
        params = {"state": "open", "sort": "created", "direction": "desc"}
        resp = get_request(
            url, headers=self.headers, params=params, output="json"
        )

        # Expression to match the head ref
        matches = jmespath.search("[*].head.label", resp)
        indx, match = next(
            (
                (indx, match)
                for (indx, match) in enumerate(matches)
                if self.head_branch in match
            ),
            (None, None),
        )

        if (indx is None) and (match is None):
            print(
                "No relevant Pull Requests found. A new Pull Request will be opened."
            )
            random_id = "".join(random.sample(string.ascii_letters, 4))
            self.head_branch = "/".join([self.head_branch, random_id])
            self.pr_exists = False
        else:
            print(
                "Relevant Pull Request found. Will push new commits to this Pull Request."
            )

            self.head_branch = match.split(":")[-1]
            self.pr_number = resp[indx]["number"]
            self.pr_exists = True

    def get_ref(self, ref):
        """Get a git reference (specifically, a HEAD ref) using GitHub's git
        database API endpoint

        Args:
            ref (str): The reference for which to return information for

        Returns:
            dict: The JSON payload response of the request
        """
        print("Pulling info for ref: {}", ref)
        url = "/".join([self.api_url, "git", "ref", "heads", ref])
        return get_request(url, headers=self.headers, output="json")
    
    def get_all_repos(self):
        """
        Get all repositories from a GitHub organization using the GitHub API
        """
        self.org_repos = []
        excluded_repos = load_excluded_repos(ignore_file=self.inputs.ignore_file)

        # First API call
        url = f"https://api.github.com/orgs/{self.org_name}/repos"
        params = {"type": "public", "per_page": 100}
        resp = get_request(url, headers=self.headers, params=params)
        for repo in resp.json():
            if repo["name"] not in excluded_repos:
                self.org_repos.append(repo["name"])

        # Paginate over results using the 'link' and rel['next'] parameters from
        # the API response
        # https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api
        while "link" in resp.headers:
            resp = get_request(
                resp.links["next"]["url"],
                headers=self.headers,
                params=params
            )
            for repo in resp.json:
              if repo["name"] not in excluded_repos:
                  self.org_repos.append(repo["name"])

    def get_contributors_from_repo(self, repo, filepath=".all-contributorsrc"):
        """Get contributors from a specific repository using the GitHub API
        
        Args:
            repo (str): The name of the repository to extract contributors from
            filepath (str): The filepath to extract contributors from (default: .all-contributorsrc)

        Returns:
            list: A list of contributors from the repository
        """
        url = f"https://api.github.com/repos/{self.org_name}/{repo}/contents/{filepath}"
        resp = get_request(url, headers=self.headers, output="json")
        resp = get_request(resp["download_url"], headers=self.input.headers, output="json")
        return resp["contributors"]
