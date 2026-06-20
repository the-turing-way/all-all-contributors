import json
import os
from os import getenv, path
from typing import Annotated

import typer

from . import git_operations, github_api
from .inject import inject_config
from .merge import merge_contributors

app = typer.Typer()


def get_github_token() -> str | None:
    """Read a GitHub token from the environment"""
    token = getenv("INPUT_GITHUB_TOKEN")
    if token is None:
        print("Environment variable INPUT_GITHUB_TOKEN is not defined")
        raise typer.Exit(code=1)
    return token


def load_excluded_repos() -> set:
    """Load excluded repositories from a file

    Returns:
        set: A set of excluded repository names
    """
    ignore_file = getenv("INPUT_IGNORE_FILE", ".repoignore")
    if path.exists(ignore_file):
        with open(ignore_file) as f:
            excluded = filter(lambda line: not line.startswith("#"), f.readlines())
    else:
        print(f"[skipping] No file found: {ignore_file}.")
        excluded = []

    return set(excluded)


@app.command()
def main(
    organisation: Annotated[
        str,
        typer.Argument(
            envvar="INPUT_ORGANISATION",
            help="Name of the GitHub organisation",
        ),
    ],
    target_repo: Annotated[
        str,
        typer.Argument(
            envvar="INPUT_TARGET_REPO",
            help="Target repository where the merged .all-contributorsrc file exists",
        ),
    ],
    target_filepath: Annotated[
        str,
        typer.Argument(
            envvar="INPUT_TARGET_FILEPATH",
            help="Target filepath where the merged .all-contributorsrc will be written",
        ),
    ] = ".all-contributorsrc",
    base_branch: Annotated[
        str,
        typer.Argument(
            envvar="INPUT_BASE_BRANCH",
            help="The name of the default branch of the target repository",
        ),
    ] = "main",
    head_branch: Annotated[
        str,
        typer.Argument(
            envvar="INPUT_HEAD_BRANCH",
            help="The name of the head branch to create in the target repository to open a Pull Request",
        ),
    ] = "merged-all-contributors",
    working_dir: Annotated[
        str,
        typer.Argument(
            envvar="INPUT_WORKING_DIR",
            help="Path to the checked-out git repository",
        ),
    ] = ".",
) -> None:
    github_token = get_github_token()
    excluded_repos = load_excluded_repos()

    # Fetch all repos from the organization
    repos = github_api.get_all_repos(organisation, github_token, excluded_repos)

    # Fetch contributors from all repos
    all_contributors = []
    for repo in repos:
        contributors = github_api.get_contributors_from_repo(
            organisation, repo, github_token
        )
        all_contributors.extend(contributors)

    # Merge contributors
    merged_contributors = merge_contributors(all_contributors)
    if not merged_contributors:
        print("No contributors to merge")
        return

    # Check if PR already exists
    pr_exists, actual_head_branch, pr_number = github_api.find_existing_pull_request(
        organisation, target_repo, head_branch, github_token
    )

    # Check if branch exists on remote
    branch_exists = git_operations.branch_exists_remote(actual_head_branch, working_dir)

    if branch_exists:
        # Checkout existing branch and pull latest changes
        print(f"Branch {actual_head_branch} exists, checking out and pulling latest")
        git_operations.checkout_branch(
            actual_head_branch, create=False, working_dir=working_dir
        )
        git_operations.pull_latest(working_dir)
    else:
        # Create new branch from current position
        print(f"Creating new branch: {actual_head_branch}")
        git_operations.checkout_branch(
            actual_head_branch, create=True, working_dir=working_dir
        )

    # Read local .all-contributorsrc file
    config_path = os.path.join(working_dir, target_filepath)
    try:
        with open(config_path, "r") as f:
            file_contents = json.load(f)
    except FileNotFoundError:
        print(f"File {target_filepath} not found, creating with default structure")
        file_contents = {
            "files": ["profile/README.md"],
            "imageSize": 100,
            "commit": False,
            "commitConvention": "angular",
            "contributors": [],
            "contributorsPerLine": 7,
            "skipCi": True,
            "repoType": "github",
            "repoHost": "https://github.com",
            "projectName": target_repo,
            "projectOwner": organisation,
        }

    # Inject merged contributors
    file_contents = inject_config(file_contents, merged_contributors)

    # Write updated .all-contributorsrc to local filesystem
    with open(config_path, "w") as f:
        json.dump(file_contents, f, indent=2)
        f.write("\n")  # Add trailing newline

    print(f"Updated {target_filepath} with merged contributors")

    # Stage modified files (ignores untracked files)
    git_operations.stage_modified_files(working_dir)

    # Create commit
    commit_message = "Merging all contributors info from across the org"
    git_operations.create_commit(commit_message, working_dir)

    # Push branch to remote
    git_operations.push_branch(actual_head_branch, working_dir)

    # Create or update pull request
    github_api.create_update_pull_request(
        organisation,
        target_repo,
        base_branch,
        actual_head_branch,
        pr_exists,
        pr_number,
        github_token,
    )


def cli():
    app()
