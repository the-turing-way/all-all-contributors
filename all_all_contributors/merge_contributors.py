"""Merge multiple .all-contributorsrc configurations into a single configuration.

This module provides functionality to merge multiple .all-contributorsrc files
into a single consolidated configuration that can be used at the organization level.
"""

from typing import List, Dict, Any
import requests
from jsonschema import validate, ValidationError


def get_all_contributors_schema() -> Dict[str, Any]:
    """Fetch the All Contributors schema from JSON Schema Store.

    Returns:
        Dict[str, Any]: The JSON schema for All Contributors configuration.
    """
    schema_url = "https://json.schemastore.org/all-contributors.json"
    response = requests.get(schema_url)
    response.raise_for_status()
    return response.json()


def merge_contributors(
    configs_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Merge multiple .all-contributorsrc configurations into a single config.

    Takes a list of complete .all-contributorsrc configurations and merges them
    into a single configuration that can be used at the organization level.
    Contributors are merged based on their profile URL, and their contributions
    types are aggregated.

    Args:
        configs_list: List of complete .all-contributorsrc configurations.
            Each config must be a valid All Contributors configuration object
            containing at least a 'contributors' array.

    Returns:
        Dict[str, Any]: A merged configuration object that follows the All
            Contributors schema, with unique contributors and their aggregated
            contributions.
    """
    # Get the schema for validation
    schema = get_all_contributors_schema()

    # Create a dictionary to store unique profiles and their contribution types
    unique_profiles = {}

    # Process each configuration
    for config in configs_list:
        try:
            # Validate the entire config against schema
            validate(instance=config, schema=schema)
        except ValidationError:
            continue

        # Process each contributor in the config
        for contributor in config.get('contributors', []):
            try:
                # Validate individual contributor against schema
                validate(instance=contributor, schema=schema['properties']['contributors']['items'])
            except ValidationError:
                continue

            profile = contributor.get('profile')
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
            contributions = contributor.get('contributions', [])
            if contributions:
                unique_profiles[profile]['contributions'].update(contributions)

    # Create the merged configuration
    merged_config = {
        'contributors': []
    }

    # Convert the dictionary to a list and convert contribution sets to lists
    for profile_data in unique_profiles.values():
        contributor = profile_data.copy()
        # Ensure at least one contribution exists
        if contributor['contributions']:
            contributor['contributions'] = sorted(
                list(contributor['contributions'])
            )
            merged_config['contributors'].append(contributor)

    return merged_config
