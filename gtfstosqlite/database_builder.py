import os
import sqlite3
import tempfile
import zipfile
from tqdm import tqdm
from gtfstosqlite.gtfs_parser import GtfsParser
from gtfstosqlite.gtfs_reference_parser import parse_reference
from gtfstosqlite.gtfs_validator import GtfsValidator


class DatabaseBuilder:
    def __init__(self):
        self.reference_database = parse_reference()

    @staticmethod
    def create_insert_statement(reference_table, rows):
        column_strings = [column.column_name for column in reference_table.columns]
        placeholders = ', '.join(['?'] * len(rows[0]))
        final_statement = (
            f"INSERT INTO {reference_table.table_name}(`{'`, `'.join(column_strings)}`) "
            f"VALUES ({placeholders})"
        )
        return final_statement

    @staticmethod
    def build_table(cur, reference_table):
        create_statement = str(reference_table)
        cur.execute(create_statement)

    def insert_data(self, cur, reference_table, rows):
        insert_statement = self.create_insert_statement(reference_table, rows)
        cur.executemany(insert_statement, rows)

    def build_database(self, con, parsed_files_list):
        cur = con.cursor()
        for filename, file in tqdm(parsed_files_list.items(), desc="Building Database", unit="file"):
            corrected_csv = GtfsValidator().correct_csv(file, filename)
            reference_table = self.reference_database.tables[filename]
            self.build_table(cur, reference_table)
            self.insert_data(cur, reference_table, corrected_csv.values.tolist())
        con.commit()

    def create_database_from_gtfs(self, input_file, output_file):
        try:
            if os.path.exists(output_file):
                os.remove(output_file)
            with sqlite3.connect(output_file) as con:
                with zipfile.ZipFile(input_file) as zip_file:
                    with tempfile.TemporaryDirectory() as tempdir:
                        zip_file.extractall(tempdir)
                        parsed_files_list = GtfsParser.parse_files(tempdir)
                        self.build_database(con, parsed_files_list)
        except Exception as e:
            raise RuntimeError(f"An error occurred: {e}")
