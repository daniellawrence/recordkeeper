#!/usr/bin/env python
import db

OPERATOR_LIST = ['=','!','<','>','~','.defined','.undefined','.in.','.nin.', \
                 '.not.', '.gt.','.lt.', '.ss.' ]


def field_divider(field_list):
    """ This will take a list of fields and split them into database_query or
    display_fields.
    a database_query request will just be the field name:
        eg. name
    a display_fields request will be a field name, operator and value
        eg. name=my_host_name
    """

    if type(field_list).__name__ == 'str':
        field_list = field_list.split()

    cli_query_list = []
    display_field_list = []

    for field in field_list:
        is_query_field = False

        # database_query fields will always have an operator.
        for operator in OPERATOR_LIST:
            if operator in field:
                is_query_field = True

        # If the field turned out to be a query then add it to the list of
        # database_queries
        if is_query_field:
            cli_query_list.append(field)
        else:
            display_field_list.append(field)

    return cli_query_list, display_field_list

def get_display_fields(field_list):
    """ Given a field_list, only return the display fields in a list. """
    cli_query_list, display_field_list = field_divider(field_list)
    return display_field_list

def get_query_fields(field_list):
    """ Given a field_list, only return the display fields in a list. """
    cli_query_list, display_field_list = field_divider(field_list)
    return cli_query_list



def generate_database_multi_update( cli_query_list ):
    if type(cli_query_list).__name__ == 'str':
        cli_query_list = cli_query_list.split(' ')

    update_dict = {'$set': {}}
    for cli_query in cli_query_list:
        (key, value) = cli_query.split('=')
        update_dict['$set'].update( {'%(key)s' % locals(): value } )
    return update_dict


def generate_database_query( cli_query ):
    """ Take a single query (eg. os=solaris) and generate a json/dict style
    filter ready for mongodb.
    The filter that is returned is a python dict.
    """

    query_operator = None
    for operator in OPERATOR_LIST:
        if operator in cli_query:
            query_operator = operator
            break

    if not query_operator:
        raise NotImplementedError(
            "Was not able to find a query_operator: %(cli_query)s" % locals())

    # If the query_operator is 'defined', create the $exists query
    if query_operator == '.defined':
        k = cli_query.split('.')[0]
        return {k: {'$exists': True }}

    # If the query_operator is 'undefined', create the $exists query
    if query_operator == '.undefined':
        k = cli_query.split('.')[0]
        return {k: {'$exists': False }}

    # Now that we have an operator, split the it into the key and the value
    # so that 'os=linux' becomes {'key': 'os', 'value': 'linux'}
    (key, value) = cli_query.split( query_operator )


    # if the type of value is a string, and it 
    if type(value).__name__ == "str" and value.lower() == "true":
        value = True

    # if the type of value is a string, and it 
    if type(value).__name__ == "str" and value.lower() == "false":
        value = False

    if value.isdigit():
        value = int(value)

    # If query is an = then simple operator
    if query_operator == "=":
        return {"%s" % key: value}

    # db.customers.find( { name : { $not : /acme.*corp/i } } );
    # { key: { $not: value } } 
    if query_operator == "!" or query_operator == ".not.":
        return {"%s" % key: {'$ne': value }}

    # db.myCollection.find( { a : { $gt: 3 } } );
    # { key: { $gt: value } } 
    #if query_operator == ">":
    if query_operator in [ ">", ".gt." ]:
        return {"%s" % key: {'$gt': int(value) }}

    # db.myCollection.find( { a : { $lt: 3 } } );
    # { "%s.value" % key: { $lt: value } } 
    if query_operator in [ "<", '.lt' ]:
        return {"%s" % key: {'$lt': int(value) }}

    if query_operator == ".ss.":
        return {"%s" % key: {'$regex': '%s' % value}}

    if query_operator == "~":
        return {"%s" % key: {'$regex': '%s' % value }}

    if query_operator == ".in.":
        return {"%s" % key: {'$in': value.split(',') }}

    if query_operator == ".nin.":
        return {"%s" % key: {'$nin': value.split(',') }}

    raise NotImplementedError("Was not able to work generate a filter: %(cli_query)s" % locals())

def generate_database_multi_query( cli_query_list ):
    """ Take a list of queries (eg. [ os=solaris , class=production ] ) and
    generate a json/dict style filter that can be used on a NoSQL database.
    The filter is then returned as a python dict(), made up of 1 or many filters.
    """

    overall_database_query = {}


    for cli_query in cli_query_list:
        database_query = generate_database_query( cli_query )
        overall_database_query.update( database_query )

    return overall_database_query


def find_records(field_list):
    cli_query_list, display_field_list = field_divider(field_list)

    # If no query, then find all!
    #if not cli_query_list:
    #    cli_query_list = ['name.defined']

    database_query = generate_database_multi_query(cli_query_list)
    rc = db.RecordKeeper()   
    record_list = rc.find(database_query, display_field_list)
    return record_list

def insert_record(record_data):
    cli_query_list, display_field_list = field_divider(record_data)
    database_query = generate_database_multi_query( cli_query_list )
    rc = db.RecordKeeper()
    new_record = rc.insert( database_query )
    return new_record

def delete_record(field_list):
    cli_query_list, display_field_list = field_divider(field_list)
    database_query = generate_database_multi_query( cli_query_list )
    rc = db.RecordKeeper()
    rc.remove( database_query )


def update_record(field_list, record_data):
    """ accept a field_list and record_data. 
    All records that match the queries in field_list will be updated with
    record_data.
    """
    cli_query_list, display_field_list = field_divider(field_list)
    database_query = generate_database_multi_query( cli_query_list )
    record_data_list, display_field_list = field_divider(record_data)
    record_data_dict = generate_database_multi_update( record_data_list )

    rc = db.RecordKeeper()
    rc.update( database_query, record_data_dict )
