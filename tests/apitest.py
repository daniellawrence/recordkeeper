#!/usr/bin/env python
import unittest
import recordkeeper.settings
import recordkeeper.api
import recordkeeper.rc_exceptions

#recordkeeper.settings.DEBUG = True


class TestApi(unittest.TestCase):

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

    def test_extract_names_from_records(self):
      	name_list = recordkeeper.api.extract_names_from_records("name=john")
        self.assertEqual(name_list, ['john'])

        record_list = recordkeeper.api.find_records("name=john")
        name_list = recordkeeper.api.extract_names_from_records(record_list)
        self.assertEqual(name_list, ['john'])

    def test_extract_names_from_records_string_query(self):
        name_list = recordkeeper.api.extract_names_from_records("sex=male")
        self.assertEqual(name_list, ['john', 'jeff', 'fred', 'sandy', 'bob'])

        record_list = recordkeeper.api.find_records("sex=male")
        name_list = recordkeeper.api.extract_names_from_records(record_list)
        self.assertEqual(name_list, ['john', 'jeff', 'fred', 'sandy', 'bob'])

    def test_relate_records_default(self):
        recordkeeper.api.relate_records("name=john", "name=fred")
        john = recordkeeper.api.find_records("name=john")
        #self.assertEqual(john, False)

