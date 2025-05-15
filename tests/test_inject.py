from all_all_contributors.inject import inject


class TestInject:
    def test_inject(self, target_all_contributors_rc_object):
        contributors = ["hello"]
        all_contributors_rc = inject(target_all_contributors_rc_object, contributors)
        assert isinstance(all_contributors_rc, dict)
        assert "contributors" in all_contributors_rc.keys()
        assert all_contributors_rc.get("contributors") == contributors
