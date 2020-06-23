import click
from faker import Faker
import sqlite_utils

fake = Faker()


@click.command()
@click.argument("db_path")
@click.option("-t", "--tables", help="Number of tables to create", default=10)
@click.option(
    "-r", "--rows", help="Number of rows to create per table", default="0,200"
)
@click.version_option()
def cli(db_path, tables, rows):
    "Tool for generating demo SQLite databases"
    db = sqlite_utils.Database(db_path)
    existing_tables = set(db.table_names())
    if not (
        rows.isdigit()
        or (rows.count(",") == 1 and all(bit.isdigit() for bit in rows.split(",")))
    ):
        raise click.ClickException("Use --rows=low,high or --rows=exact")
    if rows.isdigit():
        rows_low = rows_high = int(rows)
    else:
        rows_low, rows_high = map(int, rows.split(","))
    for i in range(tables):
        table_name = None
        while table_name is None or db[table_name].exists():
            table_name = "_".join(fake.words())
        with db.conn:
            db[table_name].create({"id": int, "name": str,}, pk="id")
            db[table_name].insert_all(
                {"name": fake.name()}
                for j in range(fake.random.randint(rows_low, rows_high))
            )
