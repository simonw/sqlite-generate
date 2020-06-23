import click
from faker import Faker
import sqlite_utils
from .utils import record_builder


class IntRange(click.ParamType):
    name = "intrange"

    def convert(self, value, param, ctx):
        if not (
            value.isdigit()
            or (
                value.count(",") == 1 and all(bit.isdigit() for bit in value.split(","))
            )
        ):
            self.fail(
                "Use --{param}=low,high or --{param}=exact",
                format(param=param),
                param,
                ctx,
            )
        if value.isdigit():
            value_low = value_high = int(value)
        else:
            value_low, value_high = map(int, value.split(","))
        return value_low, value_high


int_range = IntRange()


@click.command()
@click.argument("db_path")
@click.option("-t", "--tables", help="Number of tables to create", default=10)
@click.option(
    "-r",
    "--rows",
    help="Number of rows to create per table",
    default="0,200",
    type=int_range,
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
    if columns < 2:
        raise click.ClickException("--columns must be more than 2")
    rows_low, rows_high = rows
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
