import os
import unittest


class TestInstallationAndCommand(unittest.TestCase):

    def test_command(self):
        exit_status = os.system('gtfstosqlite ./gtfs.zip ./gtfs_test.db')
        self.assertEqual(exit_status, 0)


if __name__ == '__main__':
    unittest.main()
