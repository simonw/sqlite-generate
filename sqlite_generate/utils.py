def record_builder(fake, num_columns=2):
    "Returns {column:defs}, generator that builds records"
    assert num_columns >= 1

    # First column is always ID
    columns = ["id"]
    column_defs = {"id": int}
    column_types = [None]

    # If we have a second column, it's always name
    if num_columns >= 2:
        columns.append("name")
        column_defs["name"] = str
        column_types.append((str, fake.name))

    potential_column_types = (
        (str, fake.name),
        (str, fake.address),
        (str, fake.email),
        (int, fake.unix_time),
        (str, fake.sha1),
        (str, fake.url),
        (str, fake.zipcode),
        (str, fake.text),
        (str, lambda: str(fake.date_this_century())),
        (float, fake.pyfloat),
        (int, fake.pyint),
    )
    random_column_types = []
    if num_columns > 2:
        random_column_types = fake.random.choices(
            potential_column_types, k=num_columns - 2
        )
        column_types.extend(random_column_types)
        random_column_names = [fake.word() for _ in random_column_types]
        columns.extend(random_column_names)
        column_defs.update(
            {
                name: pair[0]
                for name, pair in zip(random_column_names, random_column_types)
            }
        )

    def generate():
        return {name: pair[1]() for name, pair in zip(columns[1:], column_types[1:])}

    return column_defs, generate
