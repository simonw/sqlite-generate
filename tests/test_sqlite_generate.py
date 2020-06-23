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


@pytest.mark.parametrize("columns", [2, 5, 10])
def test_columns(columns):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli, ["data.db", "--rows=1", "--columns={}".format(columns), "--seed=seed"]
        )
        assert 0 == result.exit_code, result.output
        db = sqlite_utils.Database("data.db")
        for table in db.tables:
            assert columns == len(table.columns)
            assert 1 == table.count


def test_seed():
    runner = CliRunner()
    with runner.isolated_filesystem():
        runner.invoke(
            cli, ["one.db", "--tables=1", "--rows=1", "--columns=2", "--seed=dog"]
        )
        runner.invoke(
            cli, ["two.db", "--tables=1", "--rows=1", "--columns=2", "--seed=dog"]
        )
        # Files should be identical
        assert open("one.db", "rb").read() == open("two.db", "rb").read()
        # With a different seed, files should differ:
        runner.invoke(
            cli, ["three.db", "--tables=1", "--rows=1", "--columns=2", "--seed=cat"]
        )
        assert open("two.db", "rb").read() != open("three.db", "rb").read()


def test_fks():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "data.db",
                "--tables=2",
                "--rows=1",
                "--columns=5",
                "--fks=2",
                "--seed=seed",
            ],
        )
        assert 0 == result.exit_code, result.output
        db = sqlite_utils.Database("data.db")
        # All tables should have columns ending in _id AND foreign keys
        for table in db.tables:
            assert table.foreign_keys
            fk_cols = [c for c in table.columns_dict if c.endswith("_id")]
            assert len(fk_cols) == 2


def test_fks_multiple_runs():
    runner = CliRunner()
    with runner.isolated_filesystem():
        for i in range(2):
            result = runner.invoke(
                cli,
                [
                    "data.db",
                    "--tables=2",
                    "--rows=1",
                    "--columns=5",
                    "--fks=2",
                    "--seed=seed{}".format(i),
                ],
            )
            assert 0 == result.exit_code, result.output
        db = sqlite_utils.Database("data.db")
        # All tables should have columns ending in _id AND foreign keys
        for table in db.tables:
            assert table.foreign_keys
            fk_cols = [c for c in table.columns_dict if c.endswith("_id")]
            assert len(fk_cols) == 2
