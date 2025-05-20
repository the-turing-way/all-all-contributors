"""Test the merge_contributors function."""

from all_all_contributors.merge import merge_contributors


def test_merge_contributors(contributor_1, contributor_2):
    """Test that the merge_contributors function merges contributors correctly."""
    contributors_list = [contributor_1, contributor_2]
    # Merge a list with duplicates
    merged_contributors = merge_contributors(
        contributors_list + contributors_list
    )
    # the merged list should just have 2 contributors
    assert len(merged_contributors) == 2
    # the merged list should have the same contributors as the original lists
    assert contributor_1 in merged_contributors
    assert contributor_2 in merged_contributors


def test_merge_contributors_duplicate(
    contributor_1, contributor_1_duplicate, contributor_2
):
    """Test that the merge_contributors function merges contributors correctly."""
    contributors_list = [contributor_1, contributor_1_duplicate, contributor_2]
    # Merge a list with duplicates
    merged_contributors = merge_contributors(contributors_list)
    # the merged list should just have 2 contributors
    assert len(merged_contributors) == 2
    # the merged list should have the same contributors as the original lists
    assert contributor_1 not in merged_contributors
    assert contributor_1_duplicate not in merged_contributors
    assert contributor_2 in merged_contributors
