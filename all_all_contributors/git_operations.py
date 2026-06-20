import os
import subprocess


def branch_exists_remote(branch_name: str, working_dir: str) -> bool:
    """
    Check if branch exists on remote.

    Args:
        branch_name: Name of the branch to check
        working_dir: Repository working directory

    Returns:
        bool: True if branch exists on remote, False otherwise
    """
    print(f"Checking if branch {branch_name} exists on remote")

    result = subprocess.run(
        ["git", "ls-remote", "--heads", "origin", branch_name],
        cwd=working_dir,
        capture_output=True,
        text=True,
        check=True,
    )

    # If output is not empty, branch exists
    return len(result.stdout.strip()) > 0


def checkout_branch(branch_name: str, create: bool, working_dir: str) -> None:
    """
    Checkout branch, optionally creating it if it doesn't exist.

    Args:
        branch_name: Name of the branch to checkout
        create: Whether to create the branch if it doesn't exist
        working_dir: Repository working directory
    """
    if create:
        print(f"Creating and checking out new branch: {branch_name}")
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=working_dir,
            check=True,
            capture_output=True,
            text=True,
        )
    else:
        print(f"Checking out existing branch: {branch_name}")
        subprocess.run(
            ["git", "checkout", branch_name],
            cwd=working_dir,
            check=True,
            capture_output=True,
            text=True,
        )


def pull_latest(working_dir: str) -> None:
    """
    Pull latest changes from remote for current branch.

    Args:
        working_dir: Repository working directory
    """
    print("Pulling latest changes from remote")

    subprocess.run(
        ["git", "pull"],
        cwd=working_dir,
        check=True,
        capture_output=True,
        text=True,
    )


def stage_modified_files(working_dir: str) -> None:
    """
    Stage all modified files (ignores untracked files).

    Uses: git add --update

    Args:
        working_dir: Repository working directory
    """
    print("Staging modified files")

    subprocess.run(
        ["git", "add", "--update"],
        cwd=working_dir,
        check=True,
        capture_output=True,
        text=True,
    )


def create_commit(message: str, working_dir: str) -> None:
    """
    Create a git commit.

    Args:
        message: Commit message
        working_dir: Repository working directory
    """
    print(f"Creating commit with message: {message}")

    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=working_dir,
        check=True,
        capture_output=True,
        text=True,
    )


def push_branch(branch_name: str, working_dir: str) -> None:
    """
    Push branch to remote (not force push).

    Args:
        branch_name: Name of the branch to push
        working_dir: Repository working directory
    """
    print(f"Pushing branch {branch_name} to remote")

    subprocess.run(
        ["git", "push", "origin", branch_name],
        cwd=working_dir,
        check=True,
        capture_output=True,
        text=True,
    )
