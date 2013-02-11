#!/usr/bin/env python
import unittest
import recordkeeper.settings
import recordkeeper.api
import recordkeeper.db
import recordkeeper.rc_exceptions

class TestDatabase(unittest.TestCase):

    def setUp(self):
        recordkeeper.settings.DATABASE_NAME = "unittest"
        recordkeeper.api.delete_record("name.defined", force=True)
        recordkeeper.api.insert_record("name=john age=1 sex=male address='key with spaces'")
        recordkeeper.api.insert_record("name=jeff age=2 sex=male")
        recordkeeper.api.insert_record("name=fred age=2 sex=male")
        recordkeeper.api.insert_record("name=sandy age=3 sex=female,male")
        recordkeeper.api.insert_record("name=bob age=3 sex=male")
        recordkeeper.api.insert_record("name=greg age=3 job=False")

    def test_find_must_have_a_query(self):
        rc = recordkeeper.db.RecordKeeper()
        with self.assertRaises(recordkeeper.rc_exceptions.InvaildQuery):
        	rc.find(database_query=None)

    def test_find_single_record(self):
    	rc = recordkeeper.db.RecordKeeper()
    	record = rc.find_one({'name': 'john'})
    	self.assertEqual(record['name'], 'john')
    	
    def test_find_record_by_id(self):
    	rc = recordkeeper.db.RecordKeeper()
    	record = rc.find_one({'name': 'john'})
    	self.assertEqual(record['name'], 'john')
    	record_id = record['_id']
    	record_2 = rc.find_one_by_id({'_id': record_id})
    	self.assertEqual( record_2, record)

    def test_remove_by_id(self):
        rc = recordkeeper.db.RecordKeeper()
    	record = rc.find_one({'name': 'john'})
    	self.assertEqual(record['name'], 'john')
    	record_id = record['_id']
    	rc.remove_by_id({'_id': record_id})
    	record = rc.find_one({'name': 'john'})
    	self.assertEqual(record, None)

    def test_db_insert(self):
    	rc = recordkeeper.db.RecordKeeper()
    	with self.assertRaises(recordkeeper.rc_exceptions.MissingRequiredInformaton):
    		rc.insert({})


