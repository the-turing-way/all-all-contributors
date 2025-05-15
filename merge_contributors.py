"""Merge multiple lists of contributors into a single list"""

import json
from typing import List, Dict, Any
import requests
from jsonschema import validate, ValidationError


def get_all_contributors_schema() -> Dict[str, Any]:
    """Fetch the All Contributors schema from JSON Schema Store.

    Returns
    -------
    Dict[str, Any]
        The JSON schema for All Contributors configuration.
    """
    schema_url = "https://json.schemastore.org/all-contributors.json"
    response = requests.get(schema_url)
    response.raise_for_status()
    return response.json()


def merge_contributors(
    contributors_list: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Merge multiple lists of contributors into a single list.

    Merge contributors extracted from multiple .all-contributorsrc files
    into a single list. Merge on the 'profile' field and make sure that
    for each unique profile, the types of contributions are aggregated.

    Parameters
    ----------
    contributors_list : List[Dict[str, Any]]
        List of contributor dictionaries. Each dictionary must contain
        the required fields: login, name, avatar_url, profile, and
        contributions. The contributions array must contain at least
        one valid contribution type.

    Returns
    -------
    List[Dict[str, Any]]
        Merged list of unique contributors with their types of contributions
        aggregated.

    Notes
    -----
    - Contributors are merged based on their profile URL
    - Contribution types are deduplicated using a set
    - The output maintains all required fields from the All Contributors schema
    - Validates against the official All Contributors JSON schema
    """
    # Get the schema for validation
    schema = get_all_contributors_schema()
    contributor_schema = schema['properties']['contributors']['items']

    # Create a dictionary to store unique profiles and their contribution types
    unique_profiles = {}

    # Process each contributor from the input list
    for contributor in contributors_list:
        try:
            # Validate contributor against schema
            validate(instance=contributor, schema=contributor_schema)
        except ValidationError:
            continue

        profile = contributor['profile']
        if not profile:
            continue

        if profile not in unique_profiles:
            # Initialize new contributor entry with required fields
            unique_profiles[profile] = {
                'login': contributor['login'],
                'name': contributor['name'],
                'avatar_url': contributor['avatar_url'],
                'profile': profile,
                'contributions': set()
            }

        # Add contributions to the set
        contributions = contributor['contributions']
        if contributions:
            unique_profiles[profile]['contributions'].update(contributions)

    # Convert the dictionary back to a list and convert contribution sets to lists
    merged_contributors = []
    for profile_data in unique_profiles.values():
        contributor = profile_data.copy()
        # Ensure at least one contribution exists
        if contributor['contributions']:
            contributor['contributions'] = sorted(
                list(contributor['contributions'])
            )
            merged_contributors.append(contributor)

    return merged_contributors




