import unittest
import gtfs_reference_parser


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.reference_database = gtfs_reference_parser.parse_reference()

    def test_table_count(self):
        self.assertEqual(len(self.reference_database.tables), 15)

    def test_table_names(self):
        reference_tables = self.reference_database.tables
        test_tables_names = ["agency", "stops", "routes", "trips", "stop_times", "calendar", "calendar_dates",
                             "fare_attributes", "fare_rules", "shapes", "frequencies", "transfers", "pathways",
                             "levels",
                             "feed_info"]
        for table, table_name in zip(reference_tables.values(), test_tables_names):
            self.assertEqual(table.table_name, table_name)

    def test_column_count(self):
        reference_tables = self.reference_database.tables
        test_columns_count = [8, 14, 12, 10, 12, 10, 3, 7, 5, 5, 5, 4, 12, 3, 9]
        for table, column_count in zip(reference_tables.values(), test_columns_count):
            self.assertEqual(len(table.columns), column_count)

    def test_primary_key(self):
        reference_agency_primary_key = self.reference_database.tables["agency"].primary_keys
        reference_routes_primary_key = self.reference_database.tables["routes"].primary_keys
        test_agency_primary_key = ["agency_id", "agency_name", "agency_url", "agency_timezone"]
        test_routes_primary_key = ["route_id", "route_type", "route_short_name", "route_long_name"]

        for reference_primary_key, test_primary_key_name in zip(reference_agency_primary_key,
                                                                test_agency_primary_key):
            self.assertEqual(reference_primary_key.column_name, test_primary_key_name)

        for reference_primary_key, test_primary_key_name in zip(reference_routes_primary_key,
                                                                test_routes_primary_key):
            self.assertEqual(reference_primary_key.column_name, test_primary_key_name)

    def test_columns_names(self):
        reference_trips_table_columns = self.reference_database.tables["trips"].columns
        test_trips_table_columns = ["route_id", "service_id", "trip_id", "trip_headsign", "trip_short_name",
                                    "direction_id", "block_id", "shape_id", "wheelchair_accessible", "bikes_allowed"]

        for column, column_name in zip(reference_trips_table_columns, test_trips_table_columns):
            self.assertEqual(column.column_name, column_name)

if __name__ == '__main__':
    unittest.main()
