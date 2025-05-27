from os import getenv, path
from pathlib import Path
from typing import Annotated, Any

import typer

from .github_api import GitHubAPI
from .inject import inject_config
from .merge import merge_contributors

app = typer.Typer()


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
        Path,
        typer.Argument(
            envvar="AAC_TARGET_REPO",
            help="Target repository where the merged .all-contributorsrc file exists",
        ),
    ],
    target_filepath: Annotated[
        Path,
        typer.Argument(
            envvar="AAC_TARGET_FILEPATH",
            help="Target filepath where the merged .all-contributorsrc will be written",
        ),
    ] = ".all-contributorsrc",
) -> None:
    github_token = get_github_token()
    excluded_repos = load_excluded_repos()

    github_api = GitHubAPI(organisation, target_repo, github_token, target_filepath)
    repos = github_api.get_all_repos(excluded_repos)

    all_contributors = []
    for repo in repos:
        contributors = github_api.get_contributors_from_repo(repo)
        all_contributors.append(contributors)

    merged_contributors = merge_contributors(all_contributors)
    if merged_contributors:
        all_contributors_rc = github_api.get_target_file_contents()
        all_contributors_rc = inject_config(all_contributors_rc, merged_contributors)


def cli():
    app()
