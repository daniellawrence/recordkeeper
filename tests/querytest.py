#!/usr/bin/env python
import unittest
import recordkeeper.settings
import recordkeeper.api
import recordkeeper.db
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

    def test_records(self):
        self.matches_excpected_records({}, 6)

    def test_query_with_spaces(self):
        self.matches_excpected_records("address='key with spaces'", 1)

        
    def test_query_for_space(self):
        self.matches_excpected_records("address~' '", 1)

    def test_query_value_has_spaces(self):
        self.matches_excpected_records("address~spaces", 1)

    def test_get_display_fields(self):
        data = recordkeeper.api.get_display_fields("name name.defined")
        self.assertEqual(data, ['name'])

    def test_get_multi_display_fields(self):
        data = recordkeeper.api.get_display_fields("name age name.defined age.defined")
        self.assertEqual(data, ['name', 'age'])

    def test_get_query_fields(self):
        data = recordkeeper.api.get_query_fields("name name.defined")
        self.assertEqual(data, ['name.defined'])

    def test_get_query_fields_multi(self):
        data = recordkeeper.api.get_query_fields("name age name.defined age.defined")
        self.assertEqual(data, ['name.defined', 'age.defined'])

    def test_query_substring(self):
        self.matches_excpected_records("sex.ss.female", 1)
        self.matches_excpected_records("sex.ss.male", 5)

    def test_subquery_gt(self):
        self.matches_excpected_records("sex=(age>1)", 5)
        self.matches_excpected_records("sex=(age<6)", 5)



    def test_key_list(self):
        rc = recordkeeper.db.RecordKeeper()
        key_list = rc.list_keys()
        self.assertEqual(key_list,['_id', 'address', 'age', 'job', 'name', 'sex'])




    def test_value_list(self):
        self.matches_excpected_records("sex=female", 1)
        self.matches_excpected_records("sex=male", 5)
        self.matches_excpected_records("sex.in.male", 5)
        self.matches_excpected_records("sex.in.female", 1)
        self.matches_excpected_records("sex.nin.male", 1)
        self.matches_excpected_records("sex.nin.female", 5)
        self.matches_excpected_records("sex!female", 5)

        self.matches_excpected_records("sex!female sex.defined", 6)
        self.matches_excpected_records("sex!male", 1)

    def test_mutilple_keys(self):
        self.matches_excpected_records("sex=female age=3", 1)
        self.matches_excpected_records("name=john age=1", 1)
        self.matches_excpected_records("name=john age=0", 0)
        #
        self.matches_excpected_records("age=1 age=3", 4)
        self.matches_excpected_records("age=1 age=2", 3)
        #
        self.matches_excpected_records("name=john name=jeff", 2)
        self.matches_excpected_records("name!john name=john", 6)

    def test_subquery(self):
        self.matches_excpected_records("age=(sex=female)", 3)
        self.matches_excpected_records("name.in.(sex=male)", 5)
        self.matches_excpected_records("name.nin.(sex=male)", 1)

        self.matches_excpected_records("sex=(name=john)", 5)
        self.matches_excpected_records("sex!(name=john)", 1)


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
        #
        self.matches_excpected_records("age.not.1", 5)
        self.matches_excpected_records("age.not.3", 3)
        self.matches_excpected_records("age.not.0", 6)

    def test_operator_equals(self):
        self.matches_excpected_records("age=1", 1)
        self.matches_excpected_records("age=2", 2)
        self.matches_excpected_records("age=3", 3)
        self.matches_excpected_records("age=0", 0)
        self.matches_excpected_records("name=john", 1)
        self.matches_excpected_records("name=bad_value", 0)

    def test_operator_notequals(self):
        self.matches_excpected_records("age!1", 5)
        self.matches_excpected_records("age!2", 4)
        self.matches_excpected_records("age!3", 3)
        self.matches_excpected_records("age!0", 6)
        self.matches_excpected_records("name!john", 5)
        self.matches_excpected_records("name!bad_value", 6)

    def test_query_as_dict(self):
        #
        self.matches_excpected_records({'age': 1}, 1)
        self.matches_excpected_records({'age': 1.0}, 1)
        #
        self.matches_excpected_records({'name': 'john'}, 1)
        self.matches_excpected_records({'name': 'bad_value'}, 0)
        #
        self.matches_excpected_records({'age': 'one'}, 0)
        self.matches_excpected_records({'age': "1"}, 0)

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

    def test_operator_regex(self):
        self.matches_excpected_records("name~john", 1)
        self.matches_excpected_records("name~match_no_records", 0)
        self.matches_excpected_records("name~^j", 2)
        self.matches_excpected_records("name~n$", 1)
        self.matches_excpected_records("name~^$", 0)
        self.matches_excpected_records("name~[0-9]", 0)
        self.matches_excpected_records("name~[A-Z]", 0)

    def test_operator_not(self):
        self.matches_excpected_records("name.not.john", 5)
        self.matches_excpected_records("name.not.match_no_records", 6)
        self.matches_excpected_records("age.not.1", 5)
        self.matches_excpected_records("age.not.3", 3)
        self.matches_excpected_records("age.not.0", 6)
        


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
        #with self.assertRaises(recordkeeper.rc_exceptions.NoRecordsFound):
        #    recordkeeper.api.find_records({'bad_key': 'bad_value'})
        self.matches_excpected_records("name=bad_value", 0)

if __name__ == '__main__':
    unittest.main()