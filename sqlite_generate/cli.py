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
@click.option(
    "--fks", help="Number of foreign keys per table", default="0,2", type=int_range
)
@click.option(
    "--fts", help="Configure full-text search (FTS5) against text columns", is_flag=True
)
@click.option(
    "--fts4",
    help="Configure full-text search (FTS4) against text columns",
    is_flag=True,
)
@click.option("--seed", help="Specify as seed for the random generator")
@click.version_option()
def cli(db_path, tables, rows, columns, fks, fts, fts4, seed):
    "Tool for generating demo SQLite databases"
    db = sqlite_utils.Database(db_path)
    existing_tables = set(db.table_names())
    fake = Faker()
    if seed:
        fake.seed_instance(seed)
    if columns < 2:
        raise click.ClickException("--columns must be more than 2")
    rows_low, rows_high = rows
    fks_low, fks_high = fks
    if not fks_high < (columns - 1):
        fks_high = columns - 1
    # Make a plan first, so we can update a progress bar
    plan = [fake.random.randint(rows_low, rows_high) for i in range(tables)]
    total_to_do = sum(plan)
    created_tables = []
    with click.progressbar(
        length=total_to_do, show_pos=True, show_percent=True, label="Generating rows"
    ) as bar:
        for num_rows in plan:
            table_name = None
            while table_name is None or db[table_name].exists():
                table_name = "_".join(fake.words())
            column_defs, generate = record_builder(
                fake,
                num_columns=columns,
                num_fks=fake.random.randint(fks_low, fks_high),
            )
            with db.conn:
                db[table_name].create(column_defs, pk="id")

                def yield_em():
                    for j in range(num_rows):
                        yield generate()
                        bar.update(1)

                db[table_name].insert_all(yield_em())
                created_tables.append(table_name)

    # Last step: populate those foreign keys
    if fks_high:
        # Find all (table, column) pairs that end in _id
        fk_columns = []
        for table_name in created_tables:
            table = db[table_name]
            for column in table.columns_dict:
                if column.endswith("_id"):
                    fk_columns.append((table_name, column))
        table_names = db.table_names()
        table_pks_cache = {}
        with click.progressbar(
            fk_columns,
            show_pos=True,
            show_percent=True,
            label="Populating foreign keys",
        ) as bar:
            for table_name, column in bar:
                other_table = fake.random.choice(table_names)
                db[table_name].add_foreign_key(column, other_table, "id")
                if other_table not in table_pks_cache:
                    table_pks_cache[other_table] = [
                        r[0]
                        for r in db.conn.execute(
                            "select id from [{}]".format(other_table)
                        ).fetchall()
                    ]
                with db.conn:
                    for row in db.conn.execute(
                        "select id from [{}]".format(table_name)
                    ).fetchall():
                        options = table_pks_cache[other_table]
                        db[table_name].update(
                            row[0],
                            {column: fake.random.choice(options) if options else None},
                        )
    if fts or fts4:
        # Configure full-text search
        with click.progressbar(
            db.tables,
            show_pos=True,
            show_percent=True,
            label="Configuring FTS{}".format("4" if fts4 else ""),
        ) as bar:
            for table in bar:
                text_columns = [
                    key for key, value in table.columns_dict.items() if value is str
                ]
                table.enable_fts(text_columns, fts_version="FTS4" if fts4 else "FTS5")
