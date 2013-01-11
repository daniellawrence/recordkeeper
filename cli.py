#!/usr/bin/env python
import re
import api

def cli_print_record(field_list):
    """ accept a list of fields (field_list), then print out the results from
    the query.
    """
    print "cli_print_record(%s)" % field_list
    try:
        record_list = api.find_records(field_list)
    except:
        print "No records found for: %s" % " ".join( field_list )
        return False

    # Grab all the display fields from the field_list
    display_field_list = api.get_display_fields(field_list)

    # Commented out, as i will assume if you have not asked for any fields,
    # then you want them all
    # Make sure that name is in the display_field_list
    #if 'name' not in display_field_list:
    #    display_field_list.append('name')

    if display_field_list:
        simple_format = re.sub('(?P<m>\w+)',"%(\g<m>)s", " ".join(display_field_list) )
        for record in record_list:
            try:
                print simple_format % record
            except KeyError:
                pass
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

def add_field(parser):
    """ completed. """
    parser.add_argument("field", type=str, nargs='+') 
    args = parser.parse_args()
    print "main(): %s" % args

    
def main():
    import argparse
    parser = argparse.ArgumentParser()
    action_group = parser.add_mutually_exclusive_group()
    parser.set_defaults(display=True)
    action_group.add_argument("--display", action="store_true")
    action_group.add_argument("--add", action="store_true")
    action_group.add_argument("--delete", action="store_true")
    action_group.add_argument("--update", action="store_true")
   # parser.add_argument("field", type=str, nargs='+') 

    args = parser.parse_args()
    print "main(): %s" % args

    if args.add:
        add_field( parser )
        return False
    return False

#    if args.delete:
#        cli_delete_record( args.field)
#        return False
#    if args.display:
#        cli_print_record( args.field)
#        return False


if __name__ == '__main__':
    main()