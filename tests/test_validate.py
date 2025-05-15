from pytest import raises
from jsonschema import ValidationError

from all_all_contributors.validate import validate_all_contributors_rc


class TestValidate:
    def test_validate_all_contributors_rc(self, target_all_contributors_rc_object):
        validate_all_contributors_rc(target_all_contributors_rc_object)

    def test_validate_all_contributors_rc_invalid(self):
        with raises(ValidationError):
            validate_all_contributors_rc({"key": "value"})
