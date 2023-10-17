![gtfs-to-sqlite](https://github.com/mbkht/gtfs-to-sqlite/actions/workflows/python-package.yml/badge.svg)
# gtfs-to-sqlite

This project provides a tool to convert GTFS (General Transit Feed Specification) data to SQLite databases for local storage and usage in mobile or desktop applications.

## Features

- Parses GTFS CSV files into Pandas DataFrames
- Validates data against the official GTFS specification
- Fixes common issues like invalid columns, wrong column order
- Builds SQLite database from parsed and validated data
- Exports SQLite schema to Android Room Entity classes

## Usage

```
python gtfstosqlite [INPUT] [OUTPUT]
```

This will parse the gtfs zip file provided in the input path, validate the data, and write the SQLite database to the output path.
