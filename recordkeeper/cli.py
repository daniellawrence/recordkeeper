#!/usr/bin/env python
import re
import argparse
import sys
import os



import api
import settings
from rc_exceptions import NoRecordsFound, DuplicateRecord, MissingRequiredInformaton, \
                          InvaildQuery, RecordKeeperException


def debug(msg):
    """ print a debug message. """
    if settings.DEBUG:
        print "DEBUG: cli.%(msg)s" % locals()

def cli_print_record( field_list, showid=False):
    """ accept a list of fields (field_list), then print out the results from
    the query.
    """
    debug("cli_print_record(%s)" % field_list)
    try:
        record_list = api.find_records(field_list)
    except NoRecordsFound as error:
        print "No records found for: %(field_list)s, %(error)s" % locals() 
        return False
    except InvaildQuery as error:
        print "Not query to query database with"
        return False

    # Grab all the display fields from the field_list
    display_field_list = api.get_display_fields(field_list)

    # Commented out, as i will assume if you have not asked for any fields,
    # then you want them all
    # Make sure that name is in the display_field_list
    #if 'name' not in display_field_list:
    #    display_field_list.append('name')

    if display_field_list:
        print " ".join(display_field_list)
        simple_format = re.sub('(?P<m>\w+)',"%(\g<m>)s", " ".join(display_field_list) )
        for record in record_list:
            try:
                print simple_format % record
            except KeyError as error:
                debug("cli_print_record: unable to print fields for record: %(error)s" % locals())
    else:
        for record in record_list:
            print "--"
            #print "name: %(name)s" % record
            for key, value in record.items():
                if type(value).__name__ in [ 'str', 'unicode','int','float','bool']:
                    print "%(key)s: %(value)s" % locals()
                    continue
                elif type(value).__name__ in [ 'list', 'set']:
                    print "%s: %s" % ( key, ",".join( value) )
                    continue
                elif type(value).__name__ == 'ObjectId':
                    if showid:
                        print "%(key)s: %(value)s" % locals()
                    continue
                elif type(value).__name__ == 'NoneType':
                    continue

                else:
                    raise RecordKeeperException("Unhandled data format '%s' <%s>" % ( key, type(value).__name__))



def cli_add_record(record_data):
    """ accept a list of fields (field_list), then print out the results from
    the query.
    """
    new_record = None
    try:
        new_record = api.insert_record( record_data)
    except DuplicateRecord as error:
        debug("%(error)s" % locals())
        print "Adding new record failed. %(error)s" % locals()
        return None
    except MissingRequiredInformaton as error:
        debug("%(error)s" % locals())
        print "Adding new record failed. %(error)s" % locals()
        return None

    return new_record

def cli_delete_record(field_list):
    """ accept a list of fields (field_list), and delete all the records that
    the query matches.
    """
    try:
        api.delete_record(field_list)
    except NoRecordsFound as error:
        print "%(error)s" % locals()
        return 


def cli_update_record(field_list, record_data):
    """ accept a field_list and record_data. 
    All records that match the queries in field_list will be updated with
    record_data.
    """
    api.update_record(field_list, record_data)

def cli_saved_queries_list():
    """ Return a list of saved queries. """
    query_list = None
    try:
        query_list = api.saved_queries_list()
    except NoRecordsFound as error:
        print "%(error)s" % locals()
        return 

    for saved_query in query_list:
        print "%s: %s" % (saved_query['name'], ' '.join(saved_query['query_data']))

def cli_saved_queries_add(query_name, query_data=None):
    """ Add a new saved query. """
    api.saved_queries_add(query_name=query_name, query_data=query_data)
    print "Create a saved query called: %(query_name)s WHERE %(query_data)s" % locals()

def cli_saved_queries_get(query_name):
    """ get a saved query. """
    query_data = None
    try:
        query_data = api.saved_queries_get(query_name=query_name)
    except NoRecordsFound as error:
        print "%(error)s" % locals()
        return 
    print " ".join(query_data)

def listkeys_args(args):
    from recordkeeper.api import list_keys
    print "\n".join(list_keys())

def print_args(args):
    parser = argparse.ArgumentParser("%s print" % sys.argv[0])
    parser.add_argument("--showid", action='store_true', default=False)
    parser.add_argument("field", type=str, nargs='+') 
    args = parser.parse_args(args)
    fields = args.field
    cli_print_record(  fields, showid=args.showid)


def query_args(args):
    parser = argparse.ArgumentParser("%s query" % sys.argv[0])
    parser.add_argument("--list", action='store_true')
    #parser.add_argument("-c", "--comment", type=str)
    parser.add_argument("query_name", type=str )
    parser.add_argument("key=value", type=str, nargs='*') 
    args = parser.parse_args(args)

    query_data = args.__dict__['key=value']
    query_name = args.query_name

    if args.list:
        cli_saved_queries_list()
        return False

    if query_data:
        cli_saved_queries_add( query_name, query_data)
        return False

    if query_name:
        cli_saved_queries_get( query_name )



def new_args(args):
    parser = argparse.ArgumentParser("%s new" % sys.argv[0])
    parser.add_argument("key=value", type=str, nargs='+') 
    args = parser.parse_args(args)
    record_data = args.__dict__['key=value']
    cli_add_record(record_data)

def update_args(args):
    parser = argparse.ArgumentParser("%s update" % sys.argv[0])
    parser.add_argument("record_data", metavar="key=new_value", type=str, nargs='+') 
    parser.add_argument("WHERE", type=str)
    parser.add_argument("field_list", metavar="query_key=query_value", type=str, nargs='+') 
    args = parser.parse_args(args)

    record_data = args.record_data
    field_list = args.field_list
    
    cli_update_record(field_list, record_data)
    cli_print_record(field_list)

def delete_args(args):
    parser = argparse.ArgumentParser("%s delete" % sys.argv[0])
    parser.add_argument("--force", action='store_true')
    parser.add_argument("key=value", type=str, nargs='+') 
    args = parser.parse_args(args)
    field_list = args.__dict__['key=value']

    if args.force:
        cli_delete_record(field_list)
    else:
        print "Missing --force, printing records"
        field_list.append('name')
        cli_print_record(field_list)




    
def main():


    args = sys.argv
    application_switch = args[0]
    application_switch = os.path.basename(args[0])

    debug("main: __file__=%(application_switch)s args=%(args)s" % locals())

    if application_switch in [ 'cli.py', 'rk_cli.py' ]:
        if len(sys.argv) == 1:
            print "Missing application switch: print, new, update delete"
            sys.exit(1)
        application_switch = sys.argv[1]
        args = args[2:]
    else:
        args = args[1:]

    if 'debug:' in application_switch:
        settings.DEBUG = True
        application_switch = application_switch.replace('debug:','')
    else:
        settings.DEBUG = False



    if application_switch in [ "print", 'rk_print.py', 'rk_print']:
        print_args(args)
        sys.exit(0)

    if application_switch  in   [ "query", 'rk_query.py', 'rk_query']:
        query_args(args)
        sys.exit(0)

    if application_switch in   [ "new", 'rk_new.py', 'rk_new']:
        new_args(args)
        sys.exit(0)

    if application_switch  in  [ "update", 'rk_update.py', 'rk_update']:
        update_args(args)
        sys.exit(0)

    if application_switch  in   [ "delete", 'rk_delete.py', 'rk_delete']:
        delete_args(args)
        sys.exit(0)

    if application_switch  in   [ "listkeys", 'rk_listkeys.py', 'rk_listkeys']:
        listkeys_args(args)
        sys.exit(0)

    print "Unknown application call %(application_switch)s" % locals()
    sys.exit(1)

if __name__ == '__main__':
    main()
