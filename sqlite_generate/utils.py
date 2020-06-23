def record_builder(fake, num_columns=1, num_pks=1, num_fks=0):
    "Returns ({column:defs}, pks-tuple, generate-fn)"
    assert num_columns >= 1

    # Primary keys come first
    if num_pks == 1:
        columns = ["id"]
    else:
        columns = ["id_{}".format(i + 1) for i in range(num_pks)]
    column_defs = {column: int for column in columns}
    column_types = [None] * num_pks
    pks = columns[:]

    # If we have a second column, it's always name
    if num_columns > num_pks:
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
    if num_columns > (num_pks + 1):
        random_column_types = fake.random.choices(
            potential_column_types, k=num_columns - 2
        )
        # If we are generating foreign keys, randomly add those now
        column_is_fk = [False] * len(random_column_types)
        if num_fks:
            random_idxs = fake.random.sample(range(len(column_is_fk)), k=num_fks)
            for idx in random_idxs:
                column_is_fk[idx] = True
                random_column_types[idx] = (int, lambda: None)

        column_types.extend(random_column_types)
        random_column_names = [
            fake.word() + ("_id" if column_is_fk[i] else "")
            for i, _ in enumerate(random_column_types)
        ]
        columns.extend(random_column_names)
        column_defs.update(
            {
                name: pair[0]
                for name, pair in zip(random_column_names, random_column_types)
            }
        )

    pk_counters = {pk: 1 for pk in pks}

    def generate():
        d = {}
        if pks:
            for pk in pks:
                d[pk] = pk_counters[pk]
            # Increment pk
            idx_to_increment = fake.random.choice(range(len(pks)))
            pk_counters[pks[idx_to_increment]] += 1
            # Reset any counters after the one we incremented
            for idx in range(idx_to_increment + 1, len(pks)):
                pk_counters[pks[idx]] = 1

        d.update(
            {
                name: pair[1]()
                for name, pair in zip(columns[len(pks) :], column_types[len(pks) :])
            }
        )
        return d

    return column_defs, pks, generate
