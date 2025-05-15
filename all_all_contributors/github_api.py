import os
import base64
import json
from http_requests import get_request

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
ORG_NAME = "the-turing-way"  
EXCLUDED_REPOS = {"repo1", "repo2"}  

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_all_repos(org, excluded):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{org}/repos"
        params = {"type": "public", "per_page": 100, "page": page}
        data = get_request(url, headers=HEADERS, params=params, output="json")
        if not data:
            break
        for repo in data:
            if repo["name"] not in excluded:
                repos.append(repo["name"])
        if len(data) < 100:
            break
        page += 1
    return repos

def get_contributors_from_repo(org, repo):
    url = f"https://api.github.com/repos/{org}/{repo}/contents/.all-contributorsrc"
    try:
        data = get_request(url, headers=HEADERS, output="json")
        if "content" in data:
            decoded = base64.b64decode(data["content"]).decode("utf-8")
            contributors = json.loads(decoded).get("contributors", [])
            return contributors
    except Exception:
        pass
    return []

def main():
    repos = get_all_repos(ORG_NAME, EXCLUDED_REPOS)
    all_contributors = {}
    for repo in repos:
        contributors = get_contributors_from_repo(ORG_NAME, repo)
        all_contributors[repo] = contributors
    print(all_contributors)

if __name__ == "__main__":
    main()
    