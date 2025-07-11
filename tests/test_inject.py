import json

from pytest import fixture, raises

from all_all_contributors.inject import inject_config
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
