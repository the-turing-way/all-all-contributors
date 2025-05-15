from typing import Any

import jsonschema
import requests


def validate_all_contributors_rc(all_contributors_rc: dict[Any]) -> None:
    """
    Validate an all contributors configuration object against the schema

    Raises:
        ValidationError: if the configuration is not valid
        SchemaError: if the schema is not valid
    """
    schema = requests.get("https://json.schemastore.org/all-contributors.json").json()
    jsonschema.validate(all_contributors_rc, schema)
