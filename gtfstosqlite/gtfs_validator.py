from re import sub

import numpy as np

from gtfstosqlite.gtfs_reference_parser import parse_reference


class GtfsValidator:

    def __init__(self):
        self.reference_database = parse_reference()

    def correct_csv(self, csv_file, filename):
        try:
            reference_table = self.reference_database.tables[filename]
        except KeyError:
            raise Exception("Table doesn't exist")

        reference_columns = reference_table.columns

        csv_file = csv_file.rename(
            columns={column: sub('^stop_id$', 'rowid', column) for column in csv_file.columns.tolist()})

        fixed_header_list = csv_file.keys()
        for column in fixed_header_list:
            if not any(column in reference_column.column_name for reference_column in reference_columns):
                csv_file = csv_file.drop(column, axis=1)

        for reference_column in reference_columns:
            if not any(reference_column.column_name in csv_column for csv_column in csv_file.keys()):
                csv_file[reference_column.column_name] = np.NAN

        columns_list = [reference_column.column_name for reference_column in reference_columns]
        csv_file = csv_file.reindex(columns=columns_list)

        return csv_file
