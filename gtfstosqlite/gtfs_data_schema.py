import os
import pathlib
import re

from caseconverter import camelcase, pascalcase

from gtfstosqlite.utils import get_kotlin_type


def parse_column_type(column_type: str):
    """
    Translates certain GTFS keywords into corresponding SQLite column types.
    """
    match column_type:
        case "INTEGER" | "ID referencing stops.stop_id" | "ID referencing routes.route_id" \
             | "Non-negative integer" | "Enum" | "ID for all tables":
            return "INTEGER"
        case "REAL" | "Latitude" | "Longitude":
            return "REAL"
        case _:
            return "TEXT"


class Column:
    def __init__(self, column_name: str, column_type: str, requirement: str):
        self.is_not_null: bool = False
        self.column_name = column_name

        # For compatibility with Android Room's FTS tables, 'stop_id' is renamed to 'rowid'
        self.column_name = re.sub('^stop_id$', 'rowid', column_name)

        self.column_type = parse_column_type(column_type)
        self.is_primary_key = False

        # A required field is necessarily not null
        if requirement == "Required":
            self.is_not_null = True

    def __repr__(self):
        """
        Generates a string representation of the column.
        """
        not_null_string = " NOT NULL" if self.is_not_null else ""
        return "`" + self.column_name + "` {}{}".format(self.column_type, not_null_string)


class Table:
    """
        Represents a database table.
        """

    def __init__(self, table_name: str, columns):
        self.table_name: str = table_name
        self.columns: list[Column] = columns
        self.primary_keys: list[str] = []

    def __repr__(self):
        """
        Generates a CREATE TABLE SQL statement for the table.
        """
        columns_string = []

        for column in self.columns:
            not_null_string = " NOT NULL" if column.is_not_null else ""
            column_string = "`" + column.column_name + "` {}{}".format(column.column_type,
                                                                       not_null_string)
            columns_string.append(column_string)

        primary_key_string = ", PRIMARY KEY({})".format(", ".join(self.primary_keys)) if self.primary_keys else ""

        final_statement = "CREATE TABLE {} (".format(self.table_name) \
                          + ", ".join(columns_string) \
                          + "{});".format(primary_key_string)
        return final_statement


class GTFSDataSchema:
    """
        Represents the schema of a GTFS database.
        """

    def __init__(self, database_name: str = "gtfs_database", tables=None):
        if tables is None:
            tables = {}
        self.database_name: str = database_name
        self.tables: dict[str, Table] = tables

    def export_to_room(self):
        """
        Exports the defined tables to Android Room Entity Kotlin files.
        """
        os.mkdir(pathlib.Path(os.getcwd() + '/kt_files'))
        for table in self.tables.values():
            with open('{}.kt'.format(os.getcwd() + '/kt_files/' + pascalcase(table.table_name)), 'w') as kt_file:
                kt_file.write('package com.example.bus_schedules.models\n\n')
                kt_file.write('import androidx.room.ColumnInfo\n')
                kt_file.write('import androidx.room.Entity\n')
                kt_file.write('import androidx.room.PrimaryKey\n\n')
                kt_file.write(
                    '@Entity(tableName = "{}")'.format(table.table_name))
                kt_file.write('\n')
                kt_file.write('data class {}(\n'.format(pascalcase(table.table_name)))
                line_str_list = []
                for column in table.columns:
                    line_str_list.append('@ColumnInfo(name = "{}") val {}: {}'.format(
                        column.column_name,
                        camelcase(column.column_name),
                        get_kotlin_type(column.column_type, column.is_not_null)
                    ))
                kt_file.write(',\n'.join(line_str_list))
                kt_file.write('\n)')
