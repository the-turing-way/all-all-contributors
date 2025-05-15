"""Test the merge_contributors function."""

import pytest
from all_all_contributors.merge import merge_contributors


def test_merge_contributors(valid_contributors_dict):
    """Test that the merge_contributors function merges contributors correctly."""
    merged_contributors = merge_contributors(
        [valid_contributors_dict, valid_contributors_dict]
    )
    # the merged list should just have 2 contributors
    assert len(merged_contributors) == 2
    # the merged list should have the same contributors as the original lists
    assert merged_contributors == [
        valid_contributors_dict["contributors"][0],
        valid_contributors_dict["contributors"][1],
    ]
