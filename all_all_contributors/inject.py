import json
from pathlib import Path
from typing import Any

from .validate import validate_all_contributors_rc


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
