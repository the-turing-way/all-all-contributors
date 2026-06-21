import json
import os
import tempfile

from pytest import fixture, raises

from all_all_contributors.inject import (
    inject_config,
    load_config_file,
    write_config_file,
)
from all_all_contributors import inject as inject_mod


@fixture()
def skip_validation(monkeypatch):
    monkeypatch.setattr(
        inject_mod,
        "validate_all_contributors_rc",
        lambda x: None,
    )


class TestInjectConfig:
    def test_inject_config(self, target_all_contributors_rc_object, skip_validation):
        contributors = ["hello"]
        all_contributors_rc = inject_config(
            target_all_contributors_rc_object, contributors
        )

        assert isinstance(all_contributors_rc, dict)
        assert "contributors" in all_contributors_rc.keys()
        assert all_contributors_rc.get("contributors") == contributors
        assert all_contributors_rc.get("projectName") == "my-project"


class TestLoadConfigFile:
    def test_loads_existing_config_file(self):
        """Test that existing config file is loaded correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, ".all-contributorsrc")
            config_data = {
                "contributors": [{"login": "user1"}],
                "projectName": "test-project",
            }
            with open(config_path, "w") as f:
                json.dump(config_data, f)

            result = load_config_file(
                config_path, ".all-contributorsrc", "test-org", "test-repo"
            )

            assert result == config_data
            assert result["projectName"] == "test-project"

    def test_creates_default_config_when_file_not_found(self):
        """Test that default config is returned when file doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, ".all-contributorsrc")

            result = load_config_file(
                config_path, ".all-contributorsrc", "test-org", "test-repo"
            )

            assert isinstance(result, dict)
            assert result["projectName"] == "test-repo"
            assert result["projectOwner"] == "test-org"
            assert result["contributors"] == []
            assert result["files"] == ["README.md"]
            assert result["imageSize"] == 100
            assert result["repoType"] == "github"


class TestWriteConfigFile:
    def test_writes_config_file_with_proper_format(self):
        """Test that config file is written with proper JSON formatting"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, ".all-contributorsrc")
            config_data = {
                "contributors": [{"login": "user1"}],
                "projectName": "test-project",
            }

            write_config_file(config_path, config_data, ".all-contributorsrc")

            # Verify file was created
            assert os.path.exists(config_path)

            # Verify contents
            with open(config_path, "r") as f:
                content = f.read()
                loaded = json.loads(content)

            assert loaded == config_data
            assert content.endswith("\n")  # Verify trailing newline

    def test_overwrites_existing_file(self):
        """Test that existing file is overwritten"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, ".all-contributorsrc")

            # Write initial content
            initial_data = {"contributors": [], "projectName": "old-name"}
            with open(config_path, "w") as f:
                json.dump(initial_data, f)

            # Overwrite with new content
            new_data = {"contributors": [{"login": "user1"}], "projectName": "new-name"}
            write_config_file(config_path, new_data, ".all-contributorsrc")

            # Verify new content
            with open(config_path, "r") as f:
                loaded = json.load(f)

            assert loaded == new_data
            assert loaded["projectName"] == "new-name"
