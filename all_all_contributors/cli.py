from os import getenv
from pathlib import Path
from typing import Annotated, Any

import typer

from .inject import inject_file

app = typer.Typer()


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
    repos = placeholder_get_org_repos(organisation, token)
    contributors = placeholder_get_contributors(repos, token)
    merged_contributors = placeholder_merge_contributors(contributors)
    if merged_contributors:
        inject_file(target, merged_contributors)


def get_github_token() -> str | None:
    token = getenv("AAC_GITHUB_TOKEN")
    if token is None:
        print("Environment variable AAC_GITHUB_TOKEN is not defined")
        raise typer.Exit(code=1)
    return token


def placeholder_get_org_repos(organisation: str, github_token: str) -> list[str]:
    ...


def placeholder_get_contributors(repos: list[str], github_token: str) -> list[Any]:
    ...


def placeholder_merge_contributors(contributors: list[Any]) -> list[Any]:
    ...


def load_excluded_repos(ignore_file=".repoignore"):
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
        print(f"[skipping] No file found: {ignore_file}.")
        excluded = []

    return set(excluded)


def cli():
    app()
