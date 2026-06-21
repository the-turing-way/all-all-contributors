import os
import subprocess


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


def stage_modified_files(working_dir: str, filepath: str = None) -> None:
    """
    Stage modified files.

    Args:
        working_dir: Repository working directory
        filepath: Optional specific file to stage. If provided, stages that file.
                  If None, stages all tracked modified files.
    """
    if filepath:
        print(f"Staging file: {filepath}")
        subprocess.run(
            ["git", "add", filepath],
            cwd=working_dir,
            check=True,
            capture_output=True,
            text=True,
        )
    else:
        print("Staging modified files")
        subprocess.run(
            ["git", "add", "--update"],
            cwd=working_dir,
            check=True,
            capture_output=True,
            text=True,
        )


def has_changes(working_dir: str, filepath: str = None) -> bool:
    """
    Check if there are any changes ready to be staged and committed.

    Args:
        working_dir: Repository working directory
        filepath: Optional specific file to check. If provided, only checks that file.
                  If None, checks all files.

    Returns:
        bool: True if there are local changes, False otherwise
    """
    cmd = ["git", "diff", "--quiet"]
    if filepath:
        cmd.append(filepath)

    result = subprocess.run(
        cmd,
        cwd=working_dir,
        capture_output=True,
        text=True,
    )

    # git diff --quiet returns 0 if no changes, 1 if there are changes
    return result.returncode == 1


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
