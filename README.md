# sqlite-generate

[![PyPI](https://img.shields.io/pypi/v/sqlite-generate.svg)](https://pypi.org/project/sqlite-generate/)
[![Changelog](https://img.shields.io/github/v/release/simonw/sqlite-generate?label=changelog)](https://github.com/simonw/sqlite-generate/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/sqlite-generate/blob/master/LICENSE)

Tool for generating demo SQLite databases

## Installation

Install this plugin using `pip`:

    $ pip install sqlite-generate

## Usage

Usage instructions go here.

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