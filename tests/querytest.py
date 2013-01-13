#!/usr/bin/env python
import unittest
import recordkeeper.settings
import recordkeeper.api
import recordkeeper.rc_exceptions

class TestQuery(unittest.TestCase):

    def setUp(self):
        recordkeeper.settings.DATABASE_NAME = "unittest"
        recordkeeper.api.delete_record({})
        recordkeeper.api.insert_record("name=john age=1 sex=male")
        recordkeeper.api.insert_record("name=jeff age=2 sex=male")
        recordkeeper.api.insert_record("name=fred age=2 sex=male")
        recordkeeper.api.insert_record("name=sandy age=3 sex=female")
        recordkeeper.api.insert_record("name=bob age=3 sex=male")
        recordkeeper.api.insert_record("name=greg age=3 job=False")

    def tearDown(self):
        recordkeeper.settings.DATABASE_NAME = "unittest"
        recordkeeper.api.delete_record({})

    def matches_excpected_records(self, query, expected_records):
        if expected_records > 0:
            all_records = recordkeeper.api.find_records(query)
            count_records = len(all_records)
            self.assertEqual(count_records, expected_records)
            return
        if expected_records == 0:
            self.matches_expected_exception(query,  recordkeeper.rc_exceptions.NoRecordsFound)

    def matches_expected_exception(self, query, expected_exception):
        with self.assertRaises(expected_exception):
            recordkeeper.api.find_records(query)

    def test_records(self):
        self.matches_excpected_records({}, 6)

    def test_value_int(self):
        self.matches_excpected_records("age=1", 1)
        self.matches_excpected_records("age=2", 2)
        self.matches_excpected_records("age=3", 3)

        self.matches_excpected_records("age<2", 1)
        self.matches_excpected_records("age<3", 3)
        self.matches_excpected_records("age<4", 6)
        #
        self.matches_excpected_records("age>1", 5)
        self.matches_excpected_records("age>2", 3)

        self.matches_excpected_records("age.in.1", 1)
        self.matches_excpected_records("age.nin.1,2", 3)
        #
        self.matches_excpected_records("age=100", 0)
        self.matches_excpected_records("age>100", 0)
        self.matches_excpected_records("age<0", 0)
        self.matches_excpected_records("age=none", 0)
        #
        self.matches_excpected_records("age.defined", 6)

    def test_operator_defined(self):
        self.matches_excpected_records("age.defined", 6)
        self.matches_excpected_records("name.defined", 6)
        self.matches_excpected_records("sex.defined", 5)
        self.matches_excpected_records("job.defined", 1)
        self.matches_excpected_records("unknown_key.defined", 0)

    def test_operator_undefined(self):
        self.matches_excpected_records("age.undefined", 0)
        self.matches_excpected_records("name.undefined", 0)
        self.matches_excpected_records("sex.undefined", 1)
        self.matches_excpected_records("job.undefined", 5)
        self.matches_excpected_records("unknown_key.undefined", 6)

    def test_operator_in(self):
        # str nin / in
        self.matches_excpected_records("name.in.john", 1)
        self.matches_excpected_records("name.in.john,jeff", 2)
        self.matches_excpected_records("name.nin.john,jeff", 4)
        # int nin / in
        self.matches_excpected_records("age.in.1", 1)
        self.matches_excpected_records("age.in.1,2", 3)
        self.matches_excpected_records("age.nin.1,2", 3)

    def test_bad_search_rasies_error(self):
        with self.assertRaises(recordkeeper.rc_exceptions.NoRecordsFound):
            recordkeeper.api.find_records({'bad_key': 'bad_value'})

if __name__ == '__main__':
    unittest.main()