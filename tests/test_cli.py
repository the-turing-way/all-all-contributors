from pytest import fixture
from typer.testing import CliRunner

from all_all_contributors.cli import app


@fixture()
def runner():
    return CliRunner()


@fixture()
def github_token(monkeypatch):
    monkeypatch.setenv("AAC_GITHUB_TOKEN", "dummy_token")


@fixture()
def unset_github_token(monkeypatch):
    monkeypatch.delenv("AAC_GITHUB_TOKEN", raising=False)


class TestCli:
    def test_cli_missing_env(self, runner, unset_github_token):
        result = runner.invoke(app, ["organisation", "./target.txt"])
        assert result.exit_code == 1
        assert "Environment variable AAC_GITHUB_TOKEN is not defined" in result.stdout
