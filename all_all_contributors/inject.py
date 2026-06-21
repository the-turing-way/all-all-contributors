import json
from pathlib import Path
from typing import Any

from .validate import validate_all_contributors_rc


def load_config_file(
    config_path: str, target_filepath: str, organisation: str, target_repo: str
) -> dict:
    """Load configuration file or create default structure

    Args:
        config_path: Full path to the config file
        target_filepath: Relative path to the config file (for display)
        organisation: GitHub organisation name
        target_repo: Target repository name

    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File {target_filepath} not found, creating with default structure")
        return {
            "files": ["README.md"],
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


def write_config_file(config_path: str, file_contents: dict, target_filepath: str) -> None:
    """Write configuration file to disk

    Args:
        config_path: Full path to the config file
        file_contents: Configuration dictionary to write
        target_filepath: Relative path to the config file (for display)
    """
    with open(config_path, "w") as f:
        json.dump(file_contents, f, indent=2)
        f.write("\n")  # Add trailing newline
    print(f"Updated {target_filepath} with merged contributors")


def inject_config(all_contributors_rc: dict[Any], contributors: list[Any]) -> dict[Any]:
    """Replace the 'contributors' field of an all contributors configuration
    JSON dict with a new list

    Returns:
        dict: Updated .all-contributorsrc config in JSON dict format
    """
    if "contributors" in all_contributors_rc.keys():
        all_contributors_rc["contributors"] = contributors
    else:
        raise AttributeError("All contributors file is missing 'contributors' field")

    validate_all_contributors_rc(all_contributors_rc)
    return all_contributors_rc
