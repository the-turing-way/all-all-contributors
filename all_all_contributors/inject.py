import json
from pathlib import Path
from typing import Any


def inject(all_contributors_rc: dict[Any], contributors: list[Any]) -> dict[Any]:
    """Replace the 'contributors' field of an all contributors configuration object with a new list"""
    if "contributors" in all_contributors_rc.keys():
        all_contributors_rc["contributors"] = contributors
    else:
        raise AttributeError("All contributors file is missing 'contributors' field")

    return all_contributors_rc


def inject_file(filepath: Path, contributors: list[Any]) -> None:
    """Replace the 'contributors' field of an all contributors configuration file with a new list"""
    with open(filepath, "r") as all_contributors_file:
        all_contributors_rc = json.load(all_contributors_file)

    all_contributors_rc = inject(all_contributors_rc, contributors)
    with open(filepath, "w") as all_contributors_file:
        json.dump(all_contributors_rc, all_contributors_file)
