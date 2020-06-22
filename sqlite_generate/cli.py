import click
from faker import Faker
import sqlite_utils

fake = Faker()


@click.command()
@click.argument("db_path")
@click.option("-t", "--tables", help="Number of tables to create", default=10)
@click.version_option()
def cli(db_path, tables):
    "Tool for generating demo SQLite databases"
    db = sqlite_utils.Database(db_path)
    existing_tables = set(db.table_names())
    for i in range(tables):
        table_name = None
        while table_name is None or db[table_name].exists():
            table_name = "_".join(fake.words())
        db[table_name].create({"id": int, "name": str,}, pk="id")
        db[table_name].insert_all(
            [{"name": fake.name()} for j in range(fake.random.randint(0, 200))]
        )
