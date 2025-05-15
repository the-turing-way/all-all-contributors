from os import getenv
from pathlib import Path
from typing import Annotated, Any

import typer

from .inject import inject_file

app = typer.Typer()


@app.command()
def merge(
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
    inject_file(target, merged_contributors)


def get_github_token() -> str | None:
    token = getenv("ACC_GITHUB_TOKEN")
    if token is None:
        raise ValueError("Environment variable ACC_GITHUB_TOKEN is not defined")
    return token


def placeholder_get_org_repos(organisation: str, github_token: str) -> list[str]:
    ...


def placeholder_get_contributors(repos: list[str], github_token: str) -> list[Any]:
    ...


def placeholder_merge_contributors(contributors: list[Any]) -> list[Any]:
    ...


def main():
    app()
