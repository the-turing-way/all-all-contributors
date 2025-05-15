from pytest import fixture
from typer.testing import CliRunner

from all_all_contributors.cli import app


@fixture()
def runner():
    return CliRunner()


@fixture()
def github_token(monkeypatch):
    monkeypatch.setenv("AAC_GITHUB_TOKEN", "dummy_token")


class TestCli:
    def test_cli(self, runner, github_token):
        result = runner.invoke(app, ["organisation", "./target.txt"])
        assert result.exit_code == 0
