"""Test the merge_contributors function."""

import pytest

from all_all_contributors.merge import (
    merge_contributors,
    merge_contributions,
    or_set,
    _unique_key,
    _contributions,
)


def contributor_in(contributor, contributor_list):
    """Check if a contributor appears in a list"""
    key = contributor.get(_unique_key)
    contributions = contributor.get(_contributions)

    for contributor_b in contributor_list:
        # Match contributor by unique key
        if contributor_b.get(_unique_key) == key:
            contributions_b = contributor_b.get(_contributions)
            if (
                # Ensure length of contributions lists are identical
                len(contributions) == len(contributions_b)
                # and that all contributions feature in each list
                and all(
                    [contribution in contributions_b for contribution in contributions]
                )
            ):
                return True
            else:
                return False

    # Return false if no matching contributor is found
    return False


class TestMergeContributors:
    def test_merge_contributors(self, contributor_1, contributor_2):
        """Test that the merge_contributors function merges contributors correctly."""
        contributors_list = [contributor_1, contributor_2]
        # Merge a list with duplicates
        merged_contributors = merge_contributors(contributors_list + contributors_list)
        # the merged list should just have 2 contributors
        assert len(merged_contributors) == 2
        # the merged list should have the same contributors as the original lists
        assert contributor_in(contributor_1, merged_contributors)
        assert contributor_in(contributor_2, merged_contributors)

    def test_merge_contributors_duplicate(
        self,
        contributor_1,
        contributor_1_duplicate,
        contributor_1_merged,
        contributor_2,
    ):
        """Test that the merge_contributors function merges contributors correctly."""
        contributors_list = [contributor_1, contributor_1_duplicate, contributor_2]
        # Merge a list with duplicates
        merged_contributors = merge_contributors(contributors_list)
        # the merged list should just have 2 contributors
        assert len(merged_contributors) == 2
        # the merged list should have contributor 2, but a merged entry for contributor 1
        assert not contributor_in(contributor_1, merged_contributors)
        assert not contributor_in(contributor_1_duplicate, merged_contributors)
        assert contributor_in(contributor_1_merged, merged_contributors)
        assert contributor_in(contributor_2, merged_contributors)


class TestMergeContributions:
    def test_merge_contributions(
        self, contributor_1, contributor_1_duplicate, contributor_1_merged
    ):
        assert merge_contributions(contributor_1, contributor_1_duplicate) == sorted(
            contributor_1_merged.get(_contributions)
        )

    def test_merge_contributions_reverse(
        self, contributor_1, contributor_1_duplicate, contributor_1_merged
    ):
        assert merge_contributions(contributor_1_duplicate, contributor_1) == sorted(
            contributor_1_merged.get(_contributions)
        )


class TestOrSet:
    @pytest.mark.parametrize(
        "first,second,result",
        [
            ([1, 2], [3, 4], [1, 2, 3, 4]),
            ([1, 2], [2, 3, 4], [1, 2, 3, 4]),
            ([1, 2], [2, 1], [1, 2]),
        ],
    )
    def test_or_set(self, first, second, result):
        assert sorted(or_set(first, second)) == sorted(result)
