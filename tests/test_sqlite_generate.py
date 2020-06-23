from click.testing import CliRunner
import pytest
from sqlite_generate.cli import cli
import sqlite_utils


def test_generate():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["data.db"])
        assert 0 == result.exit_code
        db = sqlite_utils.Database("data.db")
        assert 10 == len(db.table_names())


@pytest.mark.parametrize(
    "rows,low,high", [("--rows=20", 20, 20), ("--rows=5,500", 5, 500)]
)
def test_rows(rows, low, high):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["data.db", rows])
        assert 0 == result.exit_code, result.output
        db = sqlite_utils.Database("data.db")
        assert 10 == len(db.table_names())
        for table in db.tables:
            assert low <= table.count <= high
