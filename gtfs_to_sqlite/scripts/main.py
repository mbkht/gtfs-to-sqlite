import os
import pathlib
import re
import sqlite3
import sys
import tempfile
import zipfile
import traceback
import json
from pathlib import Path

import click
import numpy as np
import pandas
from gtfs_to_sqlite.database import Database, Table, Column
from pandas import DataFrame

from gtfs_to_sqlite.gtfs_reference_parser import parse_reference


def create_insert_statement(reference_table, rows):
    column_strings = []
    for column in reference_table.columns:
        column_strings.append(column.column_name)
    final_statement = "INSERT INTO {}(`{}`) VALUES ({}{})".format(
        reference_table.table_name,
        "`, `".join(column_strings),
        "?",
        ", ?" * (len(rows[0]) - 1)
    )
    return final_statement


def build_database(cur, reference_table: Table, dataframe):
    create_statement = str(reference_table)
    cur.execute(create_statement)
    insert_statement = create_insert_statement(reference_table, dataframe.values.tolist())
    cur.executemany(insert_statement, dataframe.values.tolist())


def correct_csv(filename: str, csv_file: DataFrame, reference_database: Database):
    # Test if the table exist in reference
    try:
        reference_table: Table = reference_database.tables[filename]
    except:
        raise Exception("Table doesn't exist")

    # Get the reference table columns
    reference_columns: list[Column] = reference_table.columns

    # rename stop_id to rowid to use Android Room FTS
    csv_file = csv_file.rename(
        columns={column: re.sub('^stop_id$', 'rowid', column) for column in csv_file.columns.tolist()})

    # check if csv file has all reference columns
    fixed_header_list = csv_file.keys()  # fixed header list because we delete items in the loop
    for column in fixed_header_list:
        if not any(column in reference_column.column_name for reference_column in reference_columns):
            csv_file = csv_file.drop(column, axis=1)

    # test reference column in csv header
    for reference_column in reference_columns:
        if not any(reference_column.column_name in csv_column for csv_column in csv_file.keys()):
            # Add empty column
            csv_file[reference_column.column_name] = np.NAN

    # Columns list in correct order
    columns_list = []
    for reference_column in reference_columns:
        columns_list.append(reference_column.column_name)

    # reorder columns
    csv_file = csv_file.reindex(columns=columns_list)

    # Find primary key candidates
    # def key_options(items):
    #     return chain.from_iterable(combinations(items, r) for r in range(1, len(items) + 1))
    #
    # for candidate in key_options(list(csv_file)[1:]):
    #     deduped = csv_file.drop_duplicates(candidate)
    #
    #     if len(deduped.index) == len(csv_file.index):
    #         print(candidate)
    #         break

    return csv_file


def parse_csv(csv_filename):
    with open(csv_filename, newline='') as csv_file:
        return pandas.read_csv(csv_file)


def parse_files(directory):
    file_list: dict[str, DataFrame] = {}
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            parsed_csv = parse_csv(f)
            file_list[Path(f).stem] = parsed_csv
    return file_list


# noinspection PyTypeChecker
def create_database_from_gtfs(input_file, output_file, reference_path=None, export_to_json=None):
    # Create the database, if it already exists, deletes it
    if os.path.exists(output_file):
        os.remove(output_file)
    con = sqlite3.connect(output_file)
    try:
        cur = con.cursor()
        zf = zipfile.ZipFile(input_file)
        with tempfile.TemporaryDirectory() as tempdir:
            zf.extractall(tempdir)
            parsed_files_list = parse_files(tempdir)

            # Database handling : if the user provided a reference file, load it. else, parse reference from
            # Google's website.
            database: Database = Database()
            if reference_path:
                print("test")
                database = database.from_JSON(reference_path)
            else:
                database = parse_reference()
            if export_to_json:
                with open(output_file, 'w') as f:
                    json.dump(database.to_JSON(), f)
                con.close()
                sys.exit(0)

            for filename, file in parsed_files_list.items():
                corrected_csv = correct_csv(filename, file, database)
                reference_table = database.tables[filename]
                build_database(cur, reference_table, corrected_csv)
        con.commit()
        con.close()
        if reference_path:
            database = database.from_JSON(reference_path)
            database.export_to_room()
    except Exception as e:
        click.echo(traceback.format_exc())
        con.close()
        os.remove(output_file)
        sys.exit(1)


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path(exists=False))
@click.option('-r', '--reference', 'reference_path', help='Path to a json reference file')
@click.option('-e', '--export', 'export_to_json', help='export the reference as a json file', is_flag = True)
def cli(input_file, output_file, reference_path, export_to_json):
    if export_to_json:
        create_database_from_gtfs(click.format_filename(input_file), click.format_filename(output_file), export_to_json=export_to_json)
    if reference_path:
        create_database_from_gtfs(click.format_filename(input_file), click.format_filename(output_file),
                                  reference_path=reference_path)
    else:
        create_database_from_gtfs(click.format_filename(input_file), click.format_filename(output_file))


if __name__ == '__main__':
    pandas.set_option('display.width', None)
    pandas.set_option('display.max_columns', None)
    cli([
        "-r" + str(pathlib.Path("reference.json")),
        str(pathlib.Path("../../gtfs.zip")),
        str(pathlib.Path("../../gtfs.db"))
    ])
