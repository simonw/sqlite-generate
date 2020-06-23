from click.testing import CliRunner
import pytest
from sqlite_generate.cli import cli
import sqlite_utils


def test_generate():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["data.db"], catch_exceptions=False)
        assert 0 == result.exit_code
        db = sqlite_utils.Database("data.db")
        assert 10 == len(db.table_names())


@pytest.mark.parametrize(
    "rows,low,high", [("--rows=20", 20, 20), ("--rows=5,500", 5, 500)]
)
def test_rows(rows, low, high):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["data.db", rows], catch_exceptions=False)
        assert 0 == result.exit_code, result.output
        db = sqlite_utils.Database("data.db")
        assert 10 == len(db.table_names())
        for table in db.tables:
            assert low <= table.count <= high


@pytest.mark.parametrize(
    "columns,low,high", [("--columns=10", 10, 10), ("--columns=5,50", 5, 50)]
)
def test_columns(columns, low, high):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            ["data.db", "--rows=1", columns, "--seed=seed"],
            catch_exceptions=False,
        )
        assert 0 == result.exit_code, result.output
        db = sqlite_utils.Database("data.db")
        for table in db.tables:
            assert low <= len(table.columns) <= high


def test_seed():
    runner = CliRunner()
    with runner.isolated_filesystem():
        runner.invoke(
            cli,
            ["one.db", "--tables=1", "--rows=1", "--columns=2", "--seed=dog"],
            catch_exceptions=False,
        )
        runner.invoke(
            cli,
            ["two.db", "--tables=1", "--rows=1", "--columns=2", "--seed=dog"],
            catch_exceptions=False,
        )
        # Files should be identical
        assert open("one.db", "rb").read() == open("two.db", "rb").read()
        # With a different seed, files should differ:
        runner.invoke(
            cli,
            ["three.db", "--tables=1", "--rows=1", "--columns=2", "--seed=cat"],
            catch_exceptions=False,
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
            catch_exceptions=False,
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
                catch_exceptions=False,
            )
            assert 0 == result.exit_code, result.output
        db = sqlite_utils.Database("data.db")
        # All tables should have columns ending in _id AND foreign keys
        for table in db.tables:
            assert table.foreign_keys
            fk_cols = [c for c in table.columns_dict if c.endswith("_id")]
            assert len(fk_cols) == 2


def test_fks_against_empty_table():
    runner = CliRunner()
    with runner.isolated_filesystem():
        runner.invoke(
            cli,
            [
                "data.db",
                "--tables=1",
                "--rows=0",
                "--columns=5",
                "--fks=0",
                "--seed=seed",
            ],
            catch_exceptions=False,
        )
        # Run it again, with fks (this used to break)
        result = runner.invoke(
            cli,
            [
                "data.db",
                "--tables=2",
                "--rows=1",
                "--columns=5",
                "--fks=2",
                "--seed=seed2",
            ],
            catch_exceptions=False,
        )
        assert 0 == result.exit_code


def test_fts():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            ["data.db", "--tables=5", "--fts", "--fks=0", "--seed=seed",],
            catch_exceptions=False,
        )
        assert 0 == result.exit_code, result.output
        db = sqlite_utils.Database("data.db")
        table_names = db.table_names()
        assert 30 == len(table_names)
        for suffix in ("_fts", "_fts_config", "_fts_data", "_fts_idx", "_fts_docsize"):
            assert any(t for t in table_names if t.endswith(suffix)), suffix


def test_fts4():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            ["data.db", "--tables=5", "--fts4", "--fks=0", "--seed=seed",],
            catch_exceptions=False,
        )
        assert 0 == result.exit_code, result.output
        db = sqlite_utils.Database("data.db")
        table_names = db.table_names()
        assert 30 == len(table_names)
        for suffix in (
            "_fts",
            "_fts_segments",
            "_fts_segdir",
            "_fts_docsize",
            "_fts_stat",
        ):
            assert any(t for t in table_names if t.endswith(suffix))
