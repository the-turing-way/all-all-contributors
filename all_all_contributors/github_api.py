import json
import random
import string
import jmespath
import requests

from .http_requests import get_request, patch_request, post_request

API_URL = "https://api.github.com"


def _get_headers(github_token: str) -> dict:
    """Get headers for GitHub API requests"""
    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {github_token}",
    }


def get_all_repos(org_name: str, github_token: str, excluded_repos: list) -> list:
    """
    Get all repositories from a GitHub organization using the GitHub API

    Args:
        org_name: The name of the GitHub organisation
        github_token: GitHub token for authentication
        excluded_repos: A list of excluded repos to skip

    Returns:
        list: A list of remaining repos in the organisation
    """
    headers = _get_headers(github_token)
    org_repos = []

    # First API call
    url = "/".join([API_URL, "orgs", org_name, "repos"])
    params = {"type": "public", "per_page": 100}
    resp = get_request(url, headers=headers, params=params)
    for repo in resp.json():
        if repo["name"] not in excluded_repos:
            org_repos.append(repo["name"])

    # Paginate over results using the 'link' and rel['next'] parameters from
    # the API response
    # https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api
    while "link" in resp.headers:
        resp = get_request(resp.links["next"]["url"], headers=headers, params=params)
        for repo in resp.json():
            if repo["name"] not in excluded_repos:
                org_repos.append(repo["name"])

    return org_repos


def get_contributors_from_repo(
    org_name: str, repo: str, github_token: str, filepath: str = ".all-contributorsrc"
) -> list:
    """Get contributors from a specific repository using the GitHub API

    Args:
        org_name: The name of the GitHub organisation
        repo: The name of the repository to extract contributors from
        github_token: GitHub token for authentication
        filepath: The filepath to extract contributors from (default: .all-contributorsrc)

    Returns:
        list: A list of contributors from the repository, or an empty list if the file doesn't exist
    """
    headers = _get_headers(github_token)
    url = "/".join([API_URL, "repos", org_name, repo, "contents", filepath])
    try:
        resp = get_request(url, headers=headers, output="json")
        resp = get_request(resp["download_url"], headers=headers, output="json")
        return resp["contributors"]
    except requests.HTTPError as e:
        if "404" in str(e):
            print(f"Skipping {repo}: {filepath} not found")
            return []
        else:
            raise


def fetch_all_contributors(org_name: str, github_token: str, repos: list) -> list:
    """Fetch contributors from all repositories

    Args:
        org_name: GitHub organisation name
        github_token: GitHub API token
        repos: List of repository names to fetch from

    Returns:
        list: All contributors from all repositories
    """
    all_contributors = []
    for repo in repos:
        contributors = get_contributors_from_repo(org_name, repo, github_token)
        all_contributors.extend(contributors)
    return all_contributors


def find_existing_pull_request(
    org_name: str, repo_name: str, head_branch: str, github_token: str
) -> tuple[bool, str, int | None]:
    """Check if the bot already has an open Pull Request

    Args:
        org_name: The name of the GitHub organisation
        repo_name: The name of the repository
        head_branch: The head branch to search for
        github_token: GitHub token for authentication

    Returns:
        tuple: (pr_exists, actual_head_branch, pr_number)
            pr_exists: True if PR exists, False otherwise
            head_branch: The head branch name (may have random suffix)
            pr_number: The PR number if exists, None otherwise
    """
    headers = _get_headers(github_token)
    print("Finding Pull Requests previously opened to merge all contributors files")

    url = "/".join([API_URL, "repos", org_name, repo_name, "pulls"])
    params = {"state": "open", "sort": "created", "direction": "desc"}
    resp = get_request(url, headers=headers, params=params, output="json")

    # Expression to match the head ref
    matches = jmespath.search("[*].head.label", resp)
    indx, match = next(
        ((indx, match) for (indx, match) in enumerate(matches) if head_branch in match),
        (None, None),
    )

    if (indx is None) and (match is None):
        print("No relevant Pull Requests found. A new Pull Request will be opened.")
        random_id = "".join(random.sample(string.ascii_letters, 4))
        actual_head_branch = "/".join([head_branch, random_id])
        return False, actual_head_branch, None
    else:
        print(
            "Relevant Pull Request found. Will push new commits to this Pull Request."
        )
        actual_head_branch = match.split(":")[-1]
        pr_number = resp[indx]["number"]
        return True, actual_head_branch, pr_number


def create_update_pull_request(
    org_name: str,
    repo_name: str,
    base_branch: str,
    head_branch: str,
    pr_exists: bool,
    pr_number: int | None,
    github_token: str,
) -> None:
    """Create or update a Pull Request via the GitHub API

    Args:
        org_name: The name of the GitHub organisation
        repo_name: The name of the repository
        base_branch: The base branch for the PR
        head_branch: The head branch for the PR
        pr_exists: Whether the PR already exists
        pr_number: The PR number if it exists
        github_token: GitHub token for authentication
    """
    headers = _get_headers(github_token)
    url = "/".join([API_URL, "repos", org_name, repo_name, "pulls"])
    pr = {
        "title": "Merging all-contributors across the org",
        "body": "",  # FIXME: Add a descriptive PR body here
        "base": base_branch,
    }

    if pr_exists:
        print("Updating Pull Request...")
        url = "/".join([url, str(pr_number)])
        pr["state"] = "open"
        resp = patch_request(
            url,
            headers=headers,
            json=pr,
            return_json=True,
        )
        print(f"Pull Request #{resp['number']} updated!")
    else:
        print("Creating Pull Request...")
        pr["head"] = head_branch
        resp = post_request(
            url,
            headers=headers,
            json=pr,
            return_json=True,
        )
        print(f"Pull Request #{resp['number']} created!")
