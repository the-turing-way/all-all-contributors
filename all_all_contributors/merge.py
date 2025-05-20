"""Merge contributors from multiple .all-contributorsrc files into a single list."""

from typing import Any

_unique_key = "profile"
_contributions = "contributions"


def merge_contributors(
    contributors_list: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Merge multiple lists of contributor dictionaries into a single list.

    This function takes a list of contributor dictionaries (typically from
    different .all-contributorsrc files) and merges them based on unique
    profile URLs. When multiple entries exist for the same contributor, their
    contributions are aggregated into a single entry.

    Args:
        contributors_list: A list of contributor dictionaries. Each contributor
            dict should have at least 'profile' and 'contributions' keys.

    Returns:
        list[dict[str, Any]]: A list of merged contributor dictionaries, where
            each contributor appears only once with their combined contributions.

    Note:
        The function merges contributors based on merge._unique_key and
        aggregates contributions types.
    """

    all_contributors = {}

    for contributor in contributors_list:
        if (key := contributor.get(_unique_key)) not in all_contributors.keys():
            all_contributors[key] = contributor.copy()
        else:
            all_contributors[key][_contributions] = list(
                set(all_contributors[key].get(_contributions) + contributor.get(_contributions))
            )

    return list(all_contributors.values())
