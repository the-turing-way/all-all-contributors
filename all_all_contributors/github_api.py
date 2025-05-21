import os
import base64
import json
import random
import string
import jmespath
from requests import put
from .http_requests import get_request, patch_request, post_request


class GitHubAPI:
    """Interact with the GitHub API and perform various git-flow tasks"""

    def __init__(self, inputs):
        self.inputs = inputs
        self.excluded_repos = _load_excluded_repos(ignore_file=inputs["ignore_file"])
        self.api_url = "/".join(
            ["https://api.github.com", "repos", self.inputs.repository]
        )

    def create_commit(self, commit_msg, contents):
        """Create a commit over the GitHub API by creating or updating a file

        Args:
            commit_msg (str): A message describing the changes the commit applies
            contents (str): The content of the file to be updated, encoded in base64
        """
        print("Committing changes to file: {}", self.inputs.filepath)
        url = "/".join([self.api_url, "contents", self.inputs.filepath])
        body = {
            "message": commit_msg,
            "content": contents,
            "sha": self.inputs.sha,
            "branch": self.inputs.head_branch,
        }
        put(url, json=body, headers=self.inputs.headers)

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
        post_request(url, headers=self.inputs.headers, json=body)

    def create_update_pull_request(self):
        """Create or update a Pull Request via the GitHub API"""
        url = "/".join([self.api_url, "pulls"])
        pr = {
            "title": "Merging all-contributors across the org",
            "body": "",  # FIXME: Add a descriptove PR body here
            "base": self.inputs.base_branch,
        }

        if self.pr_exists:
            print("Updating Pull Request...")

            url = "/".join([url, str(self.pr_number)])
            pr["state"] = "open"
            resp = patch_request(
                url,
                headers=self.inputs.headers,
                json=pr,
                return_json=True,
            )

            print(f"Pull Request #{resp['number']} updated!")
        else:
            print("Creating Pull Request...")

            pr["head"] = self.inputs.head_branch
            resp = post_request(
                url,
                headers=self.inputs.headers,
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
            url, headers=self.inputs.headers, params=params, output="json"
        )

        # Expression to match the head ref
        matches = jmespath.search("[*].head.label", resp)
        indx, match = next(
            (
                (indx, match)
                for (indx, match) in enumerate(matches)
                if self.inputs.head_branch in match
            ),
            (None, None),
        )

        if (indx is None) and (match is None):
            print(
                "No relevant Pull Requests found. A new Pull Request will be opened."
            )
            random_id = "".join(random.sample(string.ascii_letters, 4))
            self.inputs.head_branch = "/".join([self.inputs.head_branch, random_id])
            self.pr_exists = False
        else:
            print(
                "Relevant Pull Request found. Will push new commits to this Pull Request."
            )

            self.inputs.head_branch = match.split(":")[-1]
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
        return get_request(url, headers=self.inputs.headers, output="json")
    
    def get_all_repos(self):
        """
        Get all repositories from a GitHub organization using the GitHub API
        """
        self.org_repos = []

        # First API call
        url = f"https://api.github.com/orgs/{self.org_name}/repos"
        params = {"type": "public", "per_page": 100}
        resp = get_request(url, headers=self.inputs.headers, params=params)
        for repo in resp.json():
            if repo["name"] not in excluded:
                self.org_repos.append(repo["name"])

        # Paginate over results using the 'link' and rel['next'] parameters from
        # the API response
        # https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api
        while "link" in resp.headers:
            resp = get_request(
                resp.links["next"]["url"],
                headers=self.inputs.headers,
                params=params
            )
            for repo in resp.json:
              if repo["name"] not in excluded:
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
        resp = get_request(url, headers=self.inputs.headers, output="json")
        resp = get_request(resp["download_url"], headers=self.input.headers, output="json")
        return resp["contributors"]

    def _load_excluded_repos(self, ignore_file=".repoignore"):
        """Load excluded repositories from a file

        Args:
            ignore_file (str): The path to the file containing excluded repositories

        Returns:
            set: A set of excluded repository names
        """
        if os.path.exists(ignore_file):
            with open(ignore_file) as f:
                excluded = filter(lambda line: not line.startswith("#"), f.readlines())
        else:
            print(f"(skipping] No file found: {ignore_file}.")
            excluded = []

        return set(excluded)
