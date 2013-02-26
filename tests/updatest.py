#!/usr/bin/env python
import unittest
import recordkeeper.settings
import recordkeeper.api
import recordkeeper.rc_exceptions


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

    def test_simple_update_int(self):
        john = recordkeeper.api.find_records("name=john")[0]
        self.assertEqual(john['age'], 1)
        recordkeeper.api.update_record("name=john","age=100")
        john = recordkeeper.api.find_records("name=john")[0]
        self.assertEqual(int(john['age']), 100)

    def test_simple_update_as_new_key(self):
        john = recordkeeper.api.find_records("name=john")[0]
        with self.assertRaises(KeyError):
            john['NEW_KEY_FOR_TEST']
        recordkeeper.api.update_record("name=john","NEW_KEY_FOR_TEST=100")
        john = recordkeeper.api.find_records("name=john")[0]
        new_key_value = int(john['NEW_KEY_FOR_TEST'])
        self.assertEqual(new_key_value, 100)

    def test_simple_update_as_new_key_with_dict(self):
        john = recordkeeper.api.find_records("name=john")[0]
        with self.assertRaises(KeyError):
            john['NEW_KEY_FOR_TEST']
        recordkeeper.api.update_record("name=john",{'NEW_KEY_FOR_TEST': 100})
        john = recordkeeper.api.find_records("name=john")[0]
        new_key_value = int(john['NEW_KEY_FOR_TEST'])
        self.assertEqual(new_key_value, 100)
