#!/usr/bin/env python
import unittest
import recordkeeper.settings
import recordkeeper.api
import recordkeeper.rc_exceptions

class TestQuery(unittest.TestCase):

    def setUp(self):
        recordkeeper.settings.DATABASE_NAME = "unittest"
        recordkeeper.api.delete_record("name.defined", force=True)
        recordkeeper.api.insert_record("name=john age=1 sex=male address='key with spaces'")
        recordkeeper.api.insert_record("name=jeff age=2 sex=male")
        recordkeeper.api.insert_record("name=fred age=2 sex=male")
        recordkeeper.api.insert_record("name=sandy age=3 sex=female,male")
        recordkeeper.api.insert_record("name=bob age=3 sex=male")
        recordkeeper.api.insert_record("name=greg age=3 job=False")

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

    def test_add_records(self):
    	self.matches_excpected_records("name=new_john", 0)
      	recordkeeper.api.insert_record("name=new_john age=1 sex=male")
    	self.matches_excpected_records("name=new_john", 1)

    	self.matches_excpected_records("name=new_john2", 0)
      	recordkeeper.api.insert_record("name=new_john2 age=1 sex=male")
    	self.matches_excpected_records("name=new_john2", 1)

    def test_duplicate_fails(self):
    	self.matches_excpected_records("name=new_john", 0)
      	recordkeeper.api.insert_record("name=new_john age=1 sex=male")
    	self.matches_excpected_records("name=new_john", 1)

    	self.matches_excpected_records("name=new_john", 1)
    	with self.assertRaises(recordkeeper.rc_exceptions.DuplicateRecord):
      		recordkeeper.api.insert_record("name=new_john age=1 sex=male")
    	self.matches_excpected_records("name=new_john", 1)


      	self.matches_excpected_records("name=new_john", 1)
    	with self.assertRaises(recordkeeper.rc_exceptions.DuplicateRecord):
	      	recordkeeper.api.insert_record({'name': 'new_john'})
    	self.matches_excpected_records("name=new_john", 1)

    def test_without_name_fails(self):
    	with self.assertRaises(recordkeeper.rc_exceptions.MissingRequiredInformaton):
    		recordkeeper.api.insert_record("age=1 sex=male")

    	with self.assertRaises(recordkeeper.rc_exceptions.MissingRequiredInformaton):
    		recordkeeper.api.insert_record({'age': 5})

    def test_add_dict_record(self):
    	self.matches_excpected_records("name=new_john", 0)
      	recordkeeper.api.insert_record({'name': 'new_john'})
    	self.matches_excpected_records("name=new_john", 1)

    	self.matches_excpected_records("name=new_john2", 0)
      	recordkeeper.api.insert_record({'name': 'new_john2'})
    	self.matches_excpected_records("name=new_john2", 1)





if __name__ == '__main__':
    unittest.main()
