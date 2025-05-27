import base64

from os import getenv, path
from typing import Annotated, Any

import typer

from .github_api import GitHubAPI
from .inject import inject_config
from .merge import merge_contributors
from .yaml_parser import YamlParser

app = typer.Typer()
yaml = YamlParser()


def get_github_token() -> str | None:
    """Read a GitHub token from the environment"""
    token = getenv("AAC_GITHUB_TOKEN")
    if token is None:
        print("Environment variable AAC_GITHUB_TOKEN is not defined")
        raise typer.Exit(code=1)
    return token


def load_excluded_repos() -> set:
    """Load excluded repositories from a file

    Returns:
        set: A set of excluded repository names
    """
    ignore_file = getenv("AAC_IGNORE_FILE", ".repoignore")
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
            envvar="AAC_ORGANISATION",
            help="Name of the GitHub organisation",
        ),
    ],
    target_repo: Annotated[
        str,
        typer.Argument(
            envvar="AAC_TARGET_REPO",
            help="Target repository where the merged .all-contributorsrc file exists",
        ),
    ],
    target_filepath: Annotated[
        str,
        typer.Argument(
            envvar="AAC_TARGET_FILEPATH",
            help="Target filepath where the merged .all-contributorsrc will be written",
        ),
    ] = ".all-contributorsrc",
    base_branch: Annotated[
        str,
        typer.Argument(
            envvar="AAC_BASE_BRANCH",
            help="The name of the default branch of the target repository",
        ),
    ] = "main",
    head_branch: Annotated[
        str,
        typer.Argument(
            envvar="AAC_HEAD_BRANCH",
            help="The name of the head branch to create in the target repository to open a Pull Request",
        ),
    ] = "merged-all-contributors",
) -> None:
    github_token = get_github_token()
    excluded_repos = load_excluded_repos()

    github_api = GitHubAPI(
        organisation,
        target_repo,
        github_token,
        target_filepath=target_filepath,
        base_branch=base_branch,
    )
    repos = github_api.get_all_repos(excluded_repos)

    all_contributors = []
    for repo in repos:
        contributors = github_api.get_contributors_from_repo(repo)
        all_contributors.append(contributors)

    merged_contributors = merge_contributors(all_contributors)
    if merged_contributors:
        # Check if a PR exists
        github_api.find_existing_pull_request()

        # We want to work against the most up-to-date version of the target file
        if github_api.pr_exists:
            # If a PR exists, pull the file from there
            all_contributors_rc = github_api.get_target_file_contents(
                github_api.head_branch
            )
        else:
            # Otherwise, pull from the base of the repo
            all_contributors_rc = github_api.get_target_file_contents(
                github_api.base_branch
            )

        all_contributors_rc = inject_config(all_contributors_rc, merged_contributors)

        if not github_api.pr_exists:
            # Create a branch to open a PR from
            resp = github_api.get_ref(github_api.base_branch)
            github_api.create_ref(github_api.head_brach, resp["object"]["sha"])

        # base64 encode the updated config file
        encoded_all_contributors_rc = yaml.object_to_yaml_str(
            all_contributors_rc
        ).encode("utf-8")
        base64_bytes = base64.b64encode(encoded_all_contributors_rc)
        all_contributors_rc = base64_bytes.decode("utf-8")

        # Create a commit and open a pull request
        github_api.create_commit(all_contributors_rc)
        github_api.create_update_pull_request()


def cli():
    app()
