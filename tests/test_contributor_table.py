import json
import os
import subprocess
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from all_all_contributors import contributor_table


class TestGetFilesToUpdate:
    def test_returns_files_from_config(self):
        """Test that files array is extracted from config"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, ".all-contributorsrc")
            config_data = {
                "contributors": [],
                "files": ["README.md", "docs/CONTRIBUTORS.md"],
            }
            with open(config_path, "w") as f:
                json.dump(config_data, f)

            result = contributor_table.get_files_to_update(config_path)

            assert result == ["README.md", "docs/CONTRIBUTORS.md"]

    def test_returns_empty_list_when_no_files_key(self):
        """Test that empty list is returned when 'files' key is missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, ".all-contributorsrc")
            config_data = {"contributors": []}
            with open(config_path, "w") as f:
                json.dump(config_data, f)

            result = contributor_table.get_files_to_update(config_path)

            assert result == []

    def test_returns_empty_list_when_file_not_found(self):
        """Test that empty list is returned when config file doesn't exist"""
        result = contributor_table.get_files_to_update("/nonexistent/path/.all-contributorsrc")

        assert result == []

    def test_handles_invalid_json(self):
        """Test that invalid JSON is handled gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, ".all-contributorsrc")
            with open(config_path, "w") as f:
                f.write("not valid json{")

            result = contributor_table.get_files_to_update(config_path)

            assert result == []


class TestGenerateContributorTables:
    @patch("all_all_contributors.contributor_table.subprocess.run")
    @patch("all_all_contributors.contributor_table.get_files_to_update")
    def test_generates_tables_successfully(self, mock_get_files, mock_run):
        """Test successful table generation"""
        mock_get_files.return_value = ["README.md"]
        mock_run.return_value = MagicMock(stdout="Generated contributor table", stderr="")

        result = contributor_table.generate_contributor_tables("/test/repo")

        assert result == ["README.md"]
        mock_run.assert_called_once_with(
            ["all-contributors", "generate"],
            cwd="/test/repo",
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("all_all_contributors.contributor_table.subprocess.run")
    @patch("all_all_contributors.contributor_table.get_files_to_update")
    def test_returns_none_when_no_files_in_config(self, mock_get_files, mock_run):
        """Test that None is returned when no files are specified"""
        mock_get_files.return_value = []

        result = contributor_table.generate_contributor_tables("/test/repo")

        assert result is None
        mock_run.assert_not_called()

    @patch("all_all_contributors.contributor_table.subprocess.run")
    @patch("all_all_contributors.contributor_table.get_files_to_update")
    def test_handles_cli_not_found(self, mock_get_files, mock_run):
        """Test handling when all-contributors CLI is not installed"""
        mock_get_files.return_value = ["README.md"]
        mock_run.side_effect = FileNotFoundError("all-contributors not found")

        result = contributor_table.generate_contributor_tables("/test/repo")

        assert result is None

    @patch("all_all_contributors.contributor_table.subprocess.run")
    @patch("all_all_contributors.contributor_table.get_files_to_update")
    def test_handles_generation_failure(self, mock_get_files, mock_run):
        """Test handling when all-contributors generate fails"""
        mock_get_files.return_value = ["README.md"]
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["all-contributors", "generate"], stderr="Generation failed"
        )

        result = contributor_table.generate_contributor_tables("/test/repo")

        assert result is None

    @patch("all_all_contributors.contributor_table.subprocess.run")
    @patch("all_all_contributors.contributor_table.get_files_to_update")
    def test_handles_multiple_files(self, mock_get_files, mock_run):
        """Test handling multiple files to update"""
        mock_get_files.return_value = ["README.md", "docs/CONTRIBUTORS.md", "CHANGELOG.md"]
        mock_run.return_value = MagicMock(stdout="", stderr="")

        result = contributor_table.generate_contributor_tables("/test/repo")

        assert result == ["README.md", "docs/CONTRIBUTORS.md", "CHANGELOG.md"]

    @patch("all_all_contributors.contributor_table.subprocess.run")
    @patch("all_all_contributors.contributor_table.get_files_to_update")
    def test_handles_unexpected_exception(self, mock_get_files, mock_run):
        """Test handling of unexpected exceptions"""
        mock_get_files.return_value = ["README.md"]
        mock_run.side_effect = Exception("Unexpected error")

        result = contributor_table.generate_contributor_tables("/test/repo")

        assert result is None
