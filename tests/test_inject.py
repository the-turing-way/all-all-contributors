import json

from pytest import fixture, raises

from all_all_contributors.inject import inject, inject_file
from all_all_contributors import inject as inject_mod


@fixture()
def skip_validation(monkeypatch):
    monkeypatch.setattr(
        inject_mod,
        "validate_all_contributors_rc",
        lambda x: None,
    )


class TestInject:
    def test_inject(self, target_all_contributors_rc_object):
        contributors = ["hello"]
        all_contributors_rc = inject(target_all_contributors_rc_object, contributors)
        assert isinstance(all_contributors_rc, dict)
        assert "contributors" in all_contributors_rc.keys()
        assert all_contributors_rc.get("contributors") == contributors
        assert all_contributors_rc.get("projectName") == "my-project"

    def test_inject_no_contributors(self):
        contributors = ["hello"]
        with raises(AttributeError):
            inject({}, contributors)


class TestInjectFile:
    def test_inject_file(self, target_all_contributors_rc_file, skip_validation):
        contributors = ["hello"]
        inject_file(target_all_contributors_rc_file, contributors)

        with open(target_all_contributors_rc_file, "r") as infile:
            all_contributors_rc = json.load(infile)

        assert isinstance(all_contributors_rc, dict)
        assert "contributors" in all_contributors_rc.keys()
        assert all_contributors_rc.get("contributors") == contributors
        assert all_contributors_rc.get("projectName") == "my-project"
