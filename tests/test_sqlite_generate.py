from click.testing import CliRunner
from sqlite_generate.cli import cli
import sqlite_utils


def test_generate():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["data.db"])
        assert 0 == result.exit_code
        db = sqlite_utils.Database("data.db")
        assert 10 == len(db.table_names())
