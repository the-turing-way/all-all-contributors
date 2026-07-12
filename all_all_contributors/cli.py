import json
import sys

from pathlib import Path
from os import getenv, path
from typing import Annotated

import typer
import requests

from .git_cli import GitCLI, GitCLIError, verify_all_contributors_environment, run_all_contributors_generate
from .github_api import GitHubAPI
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


def read_contributors_file(
    dirpath: str = ".", filename: str = ".all-contributorsrc", full_file: bool = False
) -> list[dict]:
    """Read in the target contributors file in the target repo.

    Args:
        dirpath (str): The directory path to the contributors file
        filename (str): The name of the contributors file
        full_file (bool): If True, return the full file contents. If False, return only the contributors list.

    Returns:
        list[dict]: A list of contributor dictionaries
    Raises:
        json.JSONDecodeError: If the file is not valid JSON
    """
    filepath = Path(dirpath) / filename

    if not filepath.is_file():
        print(
            f"Warning: {filepath} does not exist, returning empty list", file=sys.stderr
        )
        return []

    try:
        with open(filepath) as f:
            contents = json.load(f)
    except json.JSONDecodeError as ex:
        raise json.JSONDecodeError(f"{filepath}: {ex.msg}", ex.doc, ex.pos) from ex

    if full_file:
        return contents

    if "contributors" not in contents.keys():
        print(
            f"Warning: {filepath} does not contain a 'contributors' key, returning empty list",
            file=sys.stderr,
        )
        return []

    return contents["contributors"]


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
    repo_dir: Annotated[
        str,
        typer.Option(
            "--repo-dir",
            envvar="INPUT_REPO_DIR",
            help="Path to the local clone of the target repository",
        ),
    ] = ".",
) -> None:
    github_token = get_github_token()
    excluded_repos = load_excluded_repos()

    git_cli = GitCLI(repo_dir=repo_dir)
    git_cli.verify_environment()
    verify_all_contributors_environment()

    github_api = GitHubAPI(
        organisation,
        target_repo,
        github_token,
        target_filepath=target_filepath,
        base_branch=base_branch,
    )

    try:
        github_api.find_existing_pull_request()
        git_cli.create_branch(github_api.head_branch, base_branch)
        repos = github_api.get_all_repos(excluded_repos)

        all_contributors = []
        for repo in repos:
            contributors = github_api.get_contributors_from_repo(repo)
            all_contributors.extend(contributors)

        # Read local contributors file
        local_contributors = read_contributors_file(dirpath=repo_dir)
        all_contributors.extend(local_contributors)

        merged_contributors = merge_contributors(all_contributors)
        if not merged_contributors:
            print("No contributors to be merged.")
            raise typer.Exit(code=0)

        aac_file_contents = read_contributors_file(dirpath=repo_dir, full_file=True)
        updated_contents = inject_config(aac_file_contents, merged_contributors)

        # Write updated file
        output_path = Path(repo_dir) / target_filepath
        with open(output_path, "w") as f:
            json.dump(updated_contents, f, indent=2)

        run_all_contributors_generate(repo_dir=repo_dir)

        if not git_cli.check_for_changes():
            print("No changes to commit.")
            raise typer.Exit(code=0)

        git_cli.commit_file(target_filepath)
        git_cli.push_branch(github_api.head_branch)
        github_api.create_update_pull_request()

    except GitCLIError as e:
        print(f"Git error: {e}", file=sys.stderr)
        raise typer.Exit(code=1)
    except requests.HTTPError as e:
        print(f"GitHub API error: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


def cli():
    app()
