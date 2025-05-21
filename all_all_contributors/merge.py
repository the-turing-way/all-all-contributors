"""Merge contributors from multiple .all-contributorsrc files into a single list."""

from typing import Any, TypeAlias

_unique_key = "profile"
_contributions = "contributions"

Contributor: TypeAlias = dict[str, Any]


def merge_contributors(
    contributors_list: list[Contributor]
) -> list[Contributor]:
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
        if (key := contributor.get(_unique_key)) in all_contributors.keys():
            all_contributors[key][_contributions] = merge_contributions(
                all_contributors[key], contributor
            )
        else:
            all_contributors[key] = contributor.copy()

    return list(all_contributors.values())


def merge_contributions(first: Contributor, second: Contributor) -> Contributor:
    """Return a sorted list of the contribution types for two contributor entries"""
    return sorted(or_set(
        first.get(_contributions),
        second.get(_contributions),
    ))


def or_set(first: list[Any], second: list[Any]) -> list[Any]:
    """Return list of values that appear in `first` or `second`"""
    return list(set(first + second))
