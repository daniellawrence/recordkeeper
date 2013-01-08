#!/usr/bin/env python
import re
import api

def cli_print_record(field_list):
    """ accept a list of fields (field_list), then print out the results from
    the query.
    """
    record_list = api.find_records(field_list)
    display_field_list = api.get_display_fields(field_list)

    # Commented out, as i will assume if you have not asked for any fields,
    # then you want them all
    # Make sure that name is in the display_field_list
    #if 'name' not in display_field_list:
    #    display_field_list.append('name')

    if display_field_list:
        simple_format = re.sub('(?P<m>\w+)',"%(\g<m>)s", " ".join(display_field_list) )
        for record in record_list:
            print simple_format % record
    else:
        for record in record_list:
            for key, value in record.items():
                print "%(key)s: %(value)s" % locals()

def cli_add_record(record_data):
    """ accept a list of fields (field_list), then print out the results from
    the query.
    """
    new_record = api.insert_record( record_data)
    return new_record

def cli_delete_record(field_list):
    """ accept a list of fields (field_list), and delete all the records that
    the query matches.
    """
    api.delete_record(field_list)

def cli_update_record(field_list, record_data):
    """ accept a field_list and record_data. 
    All records that match the queries in field_list will be updated with
    record_data.
    """
    api.update_record(field_list, record_data)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    action_group = parser.add_mutually_exclusive_group()
    parser.set_defaults(display=True)
    action_group.add_argument("--display", action="store_true")
    action_group.add_argument("--add", action="store_true")
    action_group.add_argument("--delete", action="store_true")
    action_group.add_argument("--update", action="store_true")
    parser.add_argument("field", type=str, nargs='+') 
    args = parser.parse_args()
    print args

    if args.display:
        cli_print_record( args.field)
        
    if args.display:
        cli_print_record( args.field)




if __name__ == '__main__':
    main()