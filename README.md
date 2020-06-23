# sqlite-generate

[![PyPI](https://img.shields.io/pypi/v/sqlite-generate.svg)](https://pypi.org/project/sqlite-generate/)
[![Changelog](https://img.shields.io/github/v/release/simonw/sqlite-generate?label=changelog)](https://github.com/simonw/sqlite-generate/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/sqlite-generate/blob/master/LICENSE)

Tool for generating demo SQLite databases

## Installation

Install this plugin using `pip`:

    $ pip install sqlite-generate

## Usage

To generate a SQLite database file called `data.db` with 10 randomly named tables in it, run the following:

    sqlite-generate data.db

You can see a demo of the database generated using this command running in [Datasette](https://github.com/simonw/datasette) at https://sqlite-generate-demo.datasette.io/

You can use the `--tables` option to generate a different number of tables:

    sqlite-generate data.db --tables 20

By default each table will contain a random number of rows between 0 and 200. You can customize this with the `--rows` option:

    sqlite-generate data.db --rows 20

This will insert 20 rows into each table.

    sqlite-generate data.db --tables 500,2000

This inserts a random number of rows between 500 and 2000 into each table.

Each table will have 5 columns. You can change this using `--columns`:

    sqlite-generate data.db --columns 10

You can control the random number seed used with the `--seed` option. This will result in the exact same database file being created by multiple runs of the tool:

    sqlite-generate data.db --seed=myseed

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd sqlite-generate
    python -mvenv venv
    source venv/bin/activate

Or if you are using `pipenv`:

    pipenv shell

Now install the dependencies and tests:

    pip install -e '.[test]'

To run the tests:

    pytest
