"""Merge contributors from multiple .all-contributorsrc files into a single list."""

from typing import List, Dict, Any


def merge_contributors(
    contributors_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Merge multiple 'contributors' fields into a single list.

    Takes a list of 'contributors' fields extracted from
    multiple .all-contributorsrc files and merges them into a single list.

    Args:
        contributors_list: List of 'contributors' fields.

    Returns:
        Dict[str, Any]: A merged 'contributors' list.

    Note:
        The function merges contributors based on their profile URL and
        aggregates contributions for each unique profile.
    """

    unique_profiles = []
    merged_contributors = []

    for contributors_dict in contributors_list:
        for contributor in contributors_dict["contributors"]:
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
