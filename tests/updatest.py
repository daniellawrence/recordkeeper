#!/usr/bin/env python
import unittest
import recordkeeper.settings
import recordkeeper.api
import recordkeeper.rc_exceptions

recordkeeper.settings.DEBUG = True

class TestUpdate(unittest.TestCase):

    def setUp(self):
        recordkeeper.settings.DATABASE_NAME = "unittest"
        recordkeeper.api.delete_record("name.defined", force=True)
        recordkeeper.api.insert_record("name=john age=1 sex=male address='key with spaces'")
        recordkeeper.api.insert_record("name=jeff age=2 sex=male")
        recordkeeper.api.insert_record("name=fred age=2 sex=male")
        recordkeeper.api.insert_record("name=sandy age=3 sex=female,male")
        recordkeeper.api.insert_record("name=bob age=3 sex=male")
        recordkeeper.api.insert_record("name=greg age=3 job=False")
        recordkeeper.api.debug("----------------------")

    def test_insert_list(self):
        record = recordkeeper.api.find_records("name=sandy")[0]
        self.assertEqual(record['sex'], ['female', 'male'])

    def test_dict_to_query(self):
        data = recordkeeper.api.generate_database_multi_update({'key':'value'})
        self.assertEqual(data, {'$set': {'key': 'value'}})

    def test_multi_dict_to_query(self):
        data = recordkeeper.api.generate_database_multi_update({'key':'value', 'key2': 'value2'})
        self.assertEqual(data, {'$set': {'key': 'value', 'key2': 'value2'}})

    def test_strlist_to_query(self):
        data = recordkeeper.api.generate_database_multi_update("key=1,2,3")
        self.assertEqual(data, {'$set': {'key': ['1','2','3']}})

    #def test_dict_list_to_query(self):
    #    data = recordkeeper.api.generate_database_multi_update({'key': [1,2,3]})
    #    self.assertEqual(data, {'$set': {'key': ['1','2','3']}})

    def test_dict_strlist_to_query(self):
        data = recordkeeper.api.generate_database_multi_update({'key': "1,2,3"})
        self.assertEqual(data, {'$set': {'key': ['1','2','3']}})

    def test_simple_update_int(self):
        john = recordkeeper.api.find_records("name=john")[0]
        self.assertEqual(john['age'], 1)
        recordkeeper.api.update_record("name=john", "age=100")
        john = recordkeeper.api.find_records("name=john")[0]
        self.assertEqual(int(john['age']), 100)

    def test_simple_update_str(self):
        john = recordkeeper.api.find_records("name=john")[0]
        self.assertEqual(john['age'], 1)
        recordkeeper.api.update_record("name=john", "age=string")
        john = recordkeeper.api.find_records("name=john")[0]
        self.assertEqual(john['age'], "string")

    def test_simple_update_strlist(self):
        """ Make sure that a list is not turned into a string. """
        john = recordkeeper.api.find_records("name=john")[0]
        self.assertEqual(john['age'], 1)
        recordkeeper.api.update_record("name=john", {'age': "1,2,3"})
        john = recordkeeper.api.find_records("name=john")[0]
        self.assertEqual(john['age'], ['1','2','3'])

    def test_simple_update_as_new_key(self):
        john = recordkeeper.api.find_records("name=john")[0]
        with self.assertRaises(KeyError):
            john['NEW_KEY_FOR_TEST']
        recordkeeper.api.update_record("name=john", "NEW_KEY_FOR_TEST=99")
        john = recordkeeper.api.find_records("name=john")[0]
        new_key_value = int(john['NEW_KEY_FOR_TEST'])
        self.assertEqual(new_key_value, 99)

    def test_simple_update_as_new_key_with_dict(self):
        """ Test to make sure that a dict() of {key: value} is converted to a
        mongodb query that is able to to be run against the database.
        """
        john = recordkeeper.api.find_records("name=john")[0]
        with self.assertRaises(KeyError):
            john['NEW_KEY_FOR_TEST']
        recordkeeper.api.update_record("name=john", {'NEW_KEY_FOR_TEST': 100})
        john = recordkeeper.api.find_records("name=john")[0]
        new_key_value = john['NEW_KEY_FOR_TEST']
        new_key_value = int(new_key_value)
        self.assertEqual(new_key_value, 100)
