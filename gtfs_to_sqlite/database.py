import json
import os
import pathlib
import re

from caseconverter import camelcase, pascalcase
from gtfs_to_sqlite.utils import get_kotlin_type


def parse_column_type(column_type: str):
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
        self.column_type = parse_column_type(column_type)
        self.is_primary_key = False

        # A required field is necessarily not null
        if requirement == "Required":
            self.is_not_null = True

    def __repr__(self):
        not_null_string = " NOT NULL" if self.is_not_null else ""
        return "`" + self.column_name + "` {}{}".format(self.column_type, not_null_string)

class Table:
    temp_primary_keys = {"agency": ["agency_id"],
                         "calendar": ["service_id"],
                         "calendar_dates": ["service_id", "date"],
                         "feed_info": ["feed_publisher_name"],
                         "routes": ["route_id"],
                         "shapes": ["shape_id", "shape_pt_sequence"],
                         "stops": ["rowid"],
                         "stop_times": ["trip_id", "rowid", "stop_sequence"],
                         "transfers": ["from_stop_id", "to_stop_id"],
                         "trips": ["trip_id"]
                         }

    def __init__(self, table_name: str, columns : dict[str, Column]):
        self.table_name: str = table_name
        self.columns: dict[str, Column] = columns
        self.primary_keys: list[str] = []
        for key in self.temp_primary_keys:
            if key == self.table_name:
                primary_keys = self.temp_primary_keys[key]
                self.primary_keys = primary_keys
                for primary_key in primary_keys:
                    print(",".join(key for key in self.columns))
                    self.columns[primary_key].is_primary_key = True
                    self.columns[primary_key].is_not_null = True

    def __repr__(self):
        columns_string = []

        for key in self.columns:
            not_null_string = " NOT NULL" if self.columns[key].is_not_null else ""
            column_string = "`" + self.columns[key].column_name + "` {}{}".format(self.columns[key].column_type,
                                                                       not_null_string)
            columns_string.append(column_string)

        primary_key_string = ", PRIMARY KEY({})".format(", ".join(self.primary_keys)) if self.primary_keys else ""

        final_statement = "CREATE TABLE {} (".format(self.table_name) \
                          + ", ".join(columns_string) \
                          + "{});".format(primary_key_string)
        print(final_statement)
        return final_statement


def get_room_entity_name(table : Table):
    room_entity_name = pascalcase(table.table_name)
    if room_entity_name[len(room_entity_name) - 1] == "s":
        room_entity_name = room_entity_name[:-1]
    return room_entity_name

def has_multiple_primary_keys(table : Table):
    if len(table.primary_keys) > 1:
        primary_keys_string = ','.join(['\"' + key + '\"' for key in table.primary_keys])
        return ', primaryKeys = [{}]'.format(primary_keys_string)
    else:
        return ""

class Database:

    # Constructor for the gtfs_reference_parser (also the constructor used by from_JSON)
    def __init__(self, database_name: str = "gtfs_database", tables=None):
        if tables is None:
            tables = {}
        self.database_name: str = database_name
        self.tables: dict[str, Table] = tables

    # Import the database from a json file
    @classmethod
    def from_JSON(cls, path):
        reference_file = open(path, 'r')
        reference: dict = json.loads(reference_file.read())
        table_list = {}
        for table in reference["tables"].values():
            column_list = []
            for column in table["columns"]:
                column_list.append(Column(column["column_name"], column["column_type"], column["is_not_null"]))
            table_list[table["table_name"]] = Table(table["table_name"], column_list)
            table_list[table["table_name"]].primary_keys = table["primary_keys"]
        return cls(tables=table_list)

    # Export the database to JSON
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)

    # Export the database to Android Room Entities
    def export_to_room(self):
        print('-----------\nROOM EXPORT')
        pathlib.Path(os.getcwd() + '/room_entities').mkdir(parents=True, exist_ok=True)
        exception = ["FareAttribute", "FareRule", "Frequencie", "Level", "Pathway"]
        for table in self.tables.values():
            if get_room_entity_name(table) in exception:
                print('{} NOT CREATED'.format(table.table_name))
                continue
            # Create a new file with the name of the table and the ".kt" extension
            with open('{}.kt'.format(os.getcwd() + '/room_entities/' + get_room_entity_name(table)), 'w') as kt_file:
                # Write the Room entity class for the current table in the file
                # imports
                kt_file.write('package com.example.bus_schedules.models\n\n')
                kt_file.write('import androidx.room.ColumnInfo\n')
                kt_file.write('import androidx.room.Entity\n')
                kt_file.write('import androidx.room.PrimaryKey\n\n')
                # Entity annotation
                kt_file.write(
                    '@Entity(tableName = "{}"{})'.format(table.table_name, has_multiple_primary_keys(table)))
                kt_file.write('\n')
                kt_file.write('data class {}(\n'.format(get_room_entity_name(table)))
                line_str_list = []
                # fields
                for key in table.columns:
                    primary_key_string = "@PrimaryKey " if table.columns[key].is_primary_key and len(table.primary_keys) == 1 else ""
                    line_str_list.append('\t{}@ColumnInfo(name = "{}") val {}: {}'.format(
                        primary_key_string,
                        table.columns[key].column_name,
                        camelcase(table.columns[key].column_name),
                        get_kotlin_type(table.columns[key].column_type, table.columns[key].is_not_null)
                    ))
                kt_file.write(',\n'.join(line_str_list))
                kt_file.write('\n)')