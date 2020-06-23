from setuptools import setup
import os

VERSION = "0.2"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="sqlite-generate",
    description="Tool for generating demo SQLite databases",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/sqlite-generate",
    project_urls={
        "Issues": "https://github.com/simonw/sqlite-generate/issues",
        "CI": "https://github.com/simonw/sqlite-generate/actions",
        "Changelog": "https://github.com/simonw/sqlite-generate/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["sqlite_generate"],
    entry_points="""
        [console_scripts]
        sqlite-generate=sqlite_generate.cli:cli
    """,
    install_requires=["click", "Faker", "sqlite-utils"],
    extras_require={"test": ["pytest"]},
    tests_require=["sqlite-generate[test]"],
)
