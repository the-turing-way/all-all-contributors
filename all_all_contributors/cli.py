from os import getenv
from pathlib import Path
from typing import Annotated, Any

import typer

from .inject import inject_file

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
    if os.path.exists(ignore_file):
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
    target: Annotated[
        Path,
        typer.Argument(
            envvar="AAC_TARGET",
            help="Target .all-contributorsrc file to write a merged contributors list to",
        ),
    ],
) -> None:
    token = get_github_token()
    excluded_repos = load_excluded_repos()
    repos = placeholder_get_org_repos(organisation, token)
    contributors = placeholder_get_contributors(repos, token)
    merged_contributors = placeholder_merge_contributors(contributors)
    if merged_contributors:
        inject_file(target, merged_contributors)



def placeholder_get_org_repos(organisation: str, github_token: str) -> list[str]:
    ...


def placeholder_get_contributors(repos: list[str], github_token: str) -> list[Any]:
    ...


def placeholder_merge_contributors(contributors: list[Any]) -> list[Any]:
    ...


def cli():
    app()
