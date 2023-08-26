import os
import pandas as pd


class GtfsParser:
    @staticmethod
    def parse_csv(csv_filename):
        with open(csv_filename, newline='') as csv_file:
            return pd.read_csv(csv_file)

    @staticmethod
    def parse_files(directory):
        file_list = {}
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            if os.path.isfile(f):
                parsed_csv = GtfsParser.parse_csv(f)
                file_list[os.path.splitext(filename)[0]] = parsed_csv
        return file_list