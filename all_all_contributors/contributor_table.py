"""Generate contributor tables using the all-contributors CLI."""

import json
import os
import subprocess
from typing import Optional


def get_files_to_update(config_path: str) -> list[str]:
    """Get list of files that should be updated based on .all-contributorsrc config.

    Args:
        config_path: Path to .all-contributorsrc file

    Returns:
        List of file paths from the config's 'files' array
    """
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config.get("files", [])
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Failed to parse config file: {e}")
        return []
    except Exception as e:
        print(f"Error reading config file: {e}")
        return []


def generate_contributor_tables(working_dir: str) -> Optional[list[str]]:
    """Run all-contributors generate to update contributor tables in README files.

    Args:
        working_dir: Repository working directory containing .all-contributorsrc

    Returns:
        List of file paths that were updated (relative to working_dir),
        or None if generation failed
    """
    print("Generating contributor tables...")

    # Get list of files that should be updated
    config_path = os.path.join(working_dir, ".all-contributorsrc")
    files_to_update = get_files_to_update(config_path)

    if not files_to_update:
        print("No files specified in .all-contributorsrc, skipping table generation")
        return None

    # Run all-contributors generate
    try:
        result = subprocess.run(
            ["all-contributors", "generate"],
            cwd=working_dir,
            check=True,
            capture_output=True,
            text=True,
        )
        print("Contributor tables generated successfully")
        if result.stdout:
            print(result.stdout)
        return files_to_update
    except FileNotFoundError:
        print("Error: all-contributors CLI not found")
        print("Table generation will be skipped")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running all-contributors generate: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        print("Table generation failed, continuing without tables")
        return None
    except Exception as e:
        print(f"Unexpected error during table generation: {e}")
        return None
