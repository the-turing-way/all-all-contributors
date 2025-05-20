"""Merge contributors from multiple .all-contributorsrc files into a single list."""

from typing import List, Dict, Any


def merge_contributors(
    contributors_list: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Merge multiple lists of contributor dictionaries into a single list.

    This function takes a list of contributor dictionaries (typically from
    different .all-contributorsrc files) and merges them based on unique
    profile URLs. When multiple entries exist for the same contributor, their
    contributions are aggregated into a single entry.

    Args:
        contributors_list: A list of contributor dictionaries. Each contributor
            dict should have at least 'profile' and 'contributions' keys.

    Returns:
        List[Dict[str, Any]]: A list of merged contributor dictionaries, where
            each contributor appears only once with their combined contributions.

    Note:
        The function merges contributors based on their profile URL and
        aggregates contributions for each unique profile.
    """

    unique_profiles = []
    merged_contributors = []

    for contributor in contributors_list:
        if contributor["profile"] not in unique_profiles:
            unique_profiles.append(contributor["profile"])
            merged_contributors.append(contributor)
        else:
            # find the index of the contributor in the list
            index = unique_profiles.index(contributor["profile"])
            merged_contributors[index]["contributions"].extend(
                contributor["contributions"]
            )

    return merged_contributors
