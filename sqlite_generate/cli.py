import click
from faker import Faker
import sqlite_utils
from .utils import record_builder


@click.command()
@click.argument("db_path")
@click.option("-t", "--tables", help="Number of tables to create", default=10)
@click.option(
    "-r", "--rows", help="Number of rows to create per table", default="0,200"
)
@click.option(
    "-c", "--columns", help="Number of columns to create per table", default=5
)
@click.option("--seed", help="Specify as seed for the random generator")
@click.version_option()
def cli(db_path, tables, rows, columns, seed):
    "Tool for generating demo SQLite databases"
    db = sqlite_utils.Database(db_path)
    existing_tables = set(db.table_names())
    fake = Faker()
    if seed:
        fake.seed_instance(seed)
    if not (
        rows.isdigit()
        or (rows.count(",") == 1 and all(bit.isdigit() for bit in rows.split(",")))
    ):
        raise click.ClickException("Use --rows=low,high or --rows=exact")
    if columns < 2:
        raise click.ClickException("--columns must be more than 2")
    if rows.isdigit():
        rows_low = rows_high = int(rows)
    else:
        rows_low, rows_high = map(int, rows.split(","))
    # Make a plan first, so we can update a progress bar
    plan = [fake.random.randint(rows_low, rows_high) for i in range(tables)]
    total_to_do = sum(plan)
    with click.progressbar(length=total_to_do, show_pos=True, show_percent=True) as bar:
        for num_rows in plan:
            table_name = None
            while table_name is None or db[table_name].exists():
                table_name = "_".join(fake.words())
            column_defs, generate = record_builder(fake, columns)
            with db.conn:
                db[table_name].create(column_defs, pk="id")

                def yield_em():
                    for j in range(num_rows):
                        yield generate()
                        bar.update(1)

                db[table_name].insert_all(yield_em())
