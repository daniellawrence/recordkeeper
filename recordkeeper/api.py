#!/usr/bin/env python
import db
import settings
import rc_exceptions

# List of all the 'operators' that a user is allow to do.
OPERATOR_LIST = ['=', '!', '<', '>', '~', '.defined', '.undefined', '.in.',
                 '.nin.', '.not.', '.gt.', '.lt.', '.ss.']
                 

def debug(msg):
    """ print a debug message. """
    if settings.DEBUG:
        print "DEBUG: api.%(msg)s" % locals()


def field_divider(field_list):
    """ This will take a list of fields and split them into database_query or
    display_fields.
    a database_query request will just be the field name:
        eg. name
    a display_fields request will be a field name, operator and value
        eg. name=my_host_name
    """


    field_list_type = type(field_list).__name__

    #if field_list_type == 'dict':
    #    return field_list

    #debug( "field_divider(field_list=%(field_list)s<%(field_list_type)s>)" % locals())

    if type(field_list).__name__ in ['str', 'unicode']:
        if ' ' in field_list:
            debug( "field_divider: cutting field_list='%(field_list)s'" % locals())
            import shlex
            debug("field_divider: ' ' in field_list, dividing" )
            field_list = shlex.split( field_list )
        else:
            debug( "field_divider: lone field_list='%(field_list)s'" % locals())
            new_field_list = field_list
            field_list = []
            field_list.append( new_field_list )

    #debug( "field_divider: field_list='%(field_list)s'" % locals())

    cli_query_list = []
    display_field_list = []

    for field in field_list:
        #debug( "field_divider: field='%(field)s'" % locals())
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

    debug("field_divider:cli_query_list=%(cli_query_list)s" % locals())
    debug("field_divider:display_field_list=%(display_field_list)s" % locals())
    #debug(cli_query_list)
    #debug(display_field_list)

    if not display_field_list:
        display_field_list = []
    if not cli_query_list:
        cli_query_list = []
    return (cli_query_list, display_field_list)


def get_display_fields(field_list):
    """ Given a field_list, only return the display fields in a list. """
    cli_query_list, display_field_list = field_divider(field_list)
    return display_field_list


def get_query_fields(field_list):
    """ Given a field_list, only return the display fields in a list. """
    x = field_divider(field_list)
    cli_query_list, display_field_list = field_divider(field_list)
    return cli_query_list


def generate_database_multi_update(cli_query_list):
    """ This allows the CLI to be able to send more than a single key, value for
    updates in a single statement.
    """

    if type(cli_query_list).__name__ == 'str':
        cli_query_list = cli_query_list.split(' ')


    if type(cli_query_list).__name__ == 'dict':
        tmp_query_list = []
        for key, value in cli_query_list.items():
            if type(value).__name__ in ['list', 'set']:
                for i, single_value in enumerate(value):
                    value[i] = str(single_value)
                value = ",".join(value)
            tmp_query_list.append("%(key)s=%(value)s" % locals())
        cli_query_list = tmp_query_list

    update_dict = {'$set': {}}
    for cli_query in cli_query_list:
        debug("generate_database_multi_update: %(cli_query)s" % locals())
        if '=' in cli_query:
            (key, value) = cli_query.split('=')
            if ',' in value:
                value = value.split(',')
            update_dict['$set'].update({'%(key)s' % locals(): value})

    if not update_dict['$set']:
        del update_dict['$set']

    return update_dict


def process_subquery(cli_query):
    """ If the cli_query had a subquery then this is the place that will sort
    out that mess for you.
    This allows the user to do crazy queries that have nested quires inside of
    them.
    eg.
    Find all the records where the 'age' of the record is the same as the record
    with the name of 'john'.

        age=(name=john)

    TODO: HORRBILE RE NEEDS A REFACTOR!
    """
    import re
    querydict = re.search('(?P<key>\w+)(?P<op>.*)\((?P<subkey>\w+)(?P<subop>\W+)(?P<subval>\w+)\)',cli_query).groupdict()
    subquery = "%(subkey)s%(subop)s%(subval)s" % querydict
    key = querydict['key']
    operator = querydict['op']
    query = None

    #  split up the subquery in the key, operator and value.
    sq_key, sq_op, sq_value = get_key_operator_value_from_cli_query(subquery)
    # Generate the mongodb query that will be used to gather all the subquery
    # results.
    sq_database_query = generate_database_query(sq_key, sq_op, sq_value)

    # Grab all the subquery results from the database.
    rc = db.RecordKeeper()
    sq_record_list = rc.find(sq_database_query, [key])

    sq_values_list = []

    # For each result in the subquery, loop over the record and only grab out
    # The value of the key that the query was based on.
    # In the example of:
    #     age=(name=john)
    # This will be grabbing the value of 'age' for all records that match:
    #     name=john
    for sq_value in sq_record_list:
        try:
            sq_values_list.append(sq_value[key])
        except KeyError as error:
            print "%(error)s - %(sq_value)s %(key)s" % locals()

    # The number of results is important to work out how to generate the query.
    # If there is only 1 result, then we can do an equals comparison.
    # If there is more then 1 result, then we need to do an "in" comparison.
    number_of_sq_values = len(sq_values_list)

    if number_of_sq_values == 1:
        sq_value = sq_values_list[0]
        query = "%(key)s%(operator)s%(sq_value)s" % locals()

    if number_of_sq_values > 1 and operator in ["=", '.in.']:
        filtered_sub_result = []
        for v in sq_values_list:
            filtered_sub_result.append(str(v))
        query = "%s.in.%s" % (key, ",".join(filtered_sub_result))

    if number_of_sq_values > 1 and operator in ["!", '.nin.']:
        filtered_sub_result = []
        for v in sq_values_list:
            filtered_sub_result.append(str(v))
        query = "%s.nin.%s" % (key, ",".join(filtered_sub_result))

    # If the query was a greater then operation, then we just need to grab
    # the highest value that was generated by the sub-query.
    if number_of_sq_values > 1 and operator in ['.gt.', '>']:
        filtered_sub_result = []
        for v in sq_values_list:
            try:
                filtered_sub_result.append(float(v))
            except ValueError:
                continue
        max_value = max(filtered_sub_result)
        query = "%s>%s" % (key, max_value)

    # If the query was a lower then operation, then we just need to grab
    # the lowest value that was generated by the sub-query.
    if number_of_sq_values > 1 and operator in ['.lt.', '<']:
        filtered_sub_result = []
        for v in sq_values_list:
            try:
                filtered_sub_result.append(float(v))
            except ValueError:
                continue
        min_value = min(filtered_sub_result)
        query = "%s<%s" % (key, min_value)

    debug("Turned cli_query='%(cli_query)s' into '%(query)s'" % locals())
    return query


def get_key_operator_value_from_cli_query(cli_query):
    """ Work out the key, operator and the value from a cli_query. """

    #debug("get_kov: %(cli_query)s" % locals())

    # TODO: Seams hacky. Think of a better way to do this
    if '(' in cli_query and ')' in cli_query:
        cli_query = process_subquery(cli_query)
        debug("cli_query=%(cli_query)s" % locals())

    query_operator = None
    for operator in OPERATOR_LIST:
        if operator in cli_query:
            query_operator = operator
            break

    if not query_operator:
        raise NotImplementedError(
            "Was not able to find a query_operator: %(cli_query)s" % locals())

    if query_operator in ['.defined', '.undefined']:
        key = cli_query.split('.')[0]
        value = None
    else:
        (key, value) = cli_query.split(query_operator)

    value_type = type(value).__name__

    # If the value is true or True, then convert it to a boolean
    if value_type in ["str", 'unicode'] and value.lower() == "true":
        value = True

    # If the value is false or False, then convert it to a boolean
    elif value_type in ["str", 'unicode'] and value.lower() == "false":
        value = False

    # If the value is a digit, then convert it to an int.
    elif value_type in ["str", 'unicode'] and value.isdigit():
        value = int(value)

    #debug("get_kov: %s<%s>" % (value, value_type))

    return key, query_operator, value


def generate_database_query(key, query_operator, value):
    """ Take a single query (eg. os=solaris) and generate a json/dict style
    filter ready for mongodb.
    The filter that is returned is a python dict...
        os=solaris  becomes {'os': 'solaris'}
        os!=solaris becomes {'os': {'$ne': 'solaris'}}
    """

    if query_operator == '.defined':
        return {'%s' % key: {'$exists': True}}

    # If the query_operator is 'undefined', create the $exists query
    if query_operator == '.undefined':
        return {'%s' % key: {'$exists': False}}

    # If query is an = then simple operator
    if query_operator == "=":
        return {"%s" % key: value}

    # db.customers.find( { name : { $not : /acme.*corp/i } } );
    # { key: { $not: value}}
    if query_operator == "!" or query_operator == ".not.":
        return {"%s" % key: {'$ne': value}}

    # db.myCollection.find( { a : { $gt: 3 } } );
    # { key: { $gt: value}}
    if query_operator in [">", ".gt."]:
        return {"%s" % key: {'$gt': float(value)}}

    # db.myCollection.find( { a : { $lt: 3 } } );
    # { "%s.value" % key: { $lt: value}}
    if query_operator in ["<", '.lt.']:
        return {"%s" % key: {'$lt': float(value)}}

    if query_operator == ".ss.":
        return {"%s" % key: {'$regex': '%s' % value}}

    if query_operator == "~":
        return {"%s" % key: {'$regex': '%s' % value, '$options': '-i' }}

    value_list = []

    if type(value).__name__ in ['str', 'unicode'] \
       and ',' in value and '[' in value:
        import ast
        x = ast.literal_eval(value)
        for y in x:
            if isinstance(y, str) or isinstance(y, unicode):
                value_list.append(y)
                continue
            if isinstance(y, list):
                value_list += y
                continue
    elif type(value).__name__ in ['str', 'unicode'] and ',' in value:



        value_list = value.split(',')
        for index, value in enumerate(value_list):
            try:
                value_list[index] = int(value)
            except ValueError:
                continue
    else:
        value_list = [value]

    if query_operator == ".in.":
        return {"%s" % key: {'$in': value_list}}

    if query_operator == ".nin.":
        return {"%s" % key: {'$nin': value_list}}

    raise NotImplementedError(
        "Was not able to work generate a filter: %(cli_query)s" % locals())


def generate_database_multi_query(cli_query_list):
    """ Take a list of queries (eg. [ os=solaris , class=production ] ) and
    generate a json/dict style filter that can be used on a NoSQL database.
    The filter is then returned as a python dict() and
    is made up of 1 or many filters.
    """

    overall_database_query = {}

    for cli_query in cli_query_list:
        key, operator, value = get_key_operator_value_from_cli_query(cli_query)
        #database_query = generate_database_query( cli_query )
        database_query = generate_database_query(key, operator, value)
        debug("generate_database_multi_query: %(database_query)s" % locals())

        if key not in overall_database_query:
            overall_database_query[key] = database_query
            continue

        debug("duplicate key=%(key)s" % locals())
        old_key_query = overall_database_query[key]
        if old_key_query == database_query:
            continue
        key_or = {'$or': [old_key_query, database_query]}
        overall_database_query[key] = key_or

    real_database_query = {}
    for key, key_query in overall_database_query.items():
        real_database_query.update(key_query)

    return real_database_query


def find_records(field_list):
    """ Given a list of fields, find all the records that match queries in the
    field_list.
    """
    debug("find_records(%s)" % field_list)

    database_query = None
    display_field_list = None

    # If the record data is a string then convert it to a dict()
    if type(field_list).__name__ in ['str', 'unicode']:
        # replaced the .split() with the shelx.split() so that quotes are
        #respected.
        #field_list = field_list.split()
        import shlex
        field_list = shlex.split(field_list)

    if type(field_list).__name__ in ['list']:
        cli_query_list, display_field_list = field_divider(field_list)
        database_query = generate_database_multi_query(cli_query_list)
        cli_query_list, display_field_list = field_divider(field_list)
        debug("find_Records cli_query_list=%(cli_query_list)s" % locals())
        debug("find_Records display_field_list=%(display_field_list)s" % locals())
        database_query = generate_database_multi_query(cli_query_list)
        
    # If the record_data is already a dict, then add it to the database.
    if type(field_list).__name__ in ['dict']:
        database_query = field_list

    # If no query, then find all!
    #if not cli_query_list:
    #    cli_query_list = ['name.defined']

    debug("find_records: database_query=%(database_query)s" % locals())

    rc = db.RecordKeeper()
    record_list = rc.find(database_query, display_field_list)
    return record_list


def insert_record(record_data):
    """ accept a string of key=value pairs or a dict() of {key: value} pairs and
    add them to the records database.
    """
    database_query = None

    debug("insert_record(%(record_data)s)" % locals())

    # If the record data is a string then convert it to a dict()
    if type(record_data).__name__ in ['str', 'unicode']:
        #record_data = record_data.split()
        import shlex
        record_data = shlex.split(record_data)

    if type(record_data).__name__ in ['list']:
        cli_query_list, display_field_list = field_divider(record_data)
        database_query = generate_database_multi_query(cli_query_list)

        debug("")

    # If the record_data is already a dict, then add it to the database.
    if type(record_data).__name__ in ['dict']:
        database_query = record_data

    rc = db.RecordKeeper()
    new_record = rc.insert(database_query)
    return new_record


def delete_record(field_list, force=False):
    #cli_query_list, display_field_list = field_divider(field_list)
    #database_query = generate_database_multi_query( cli_query_list )
    database_query = None

    # If the record data is a string then convert it to a dict()
    if type(field_list).__name__ in ['str', 'unicode', 'list']:
        cli_query_list, display_field_list = field_divider(field_list)
        database_query = generate_database_multi_query(cli_query_list)
        
    # If the record_data is already a dict, then add it to the database.
    if type(field_list).__name__ in ['dict']:
        database_query = field_list

    if not database_query:
        raise rc_exceptions.InvaildQuery("Didn't build a query from '%(field_list)s'" % locals())

    rc = db.RecordKeeper()
    rc.remove(database_query, force = force)


def update_record(field_list, raw_record_data):
    """ accept a field_list and record_data.
    All records that match the queries in field_list will be updated with
    record_data.
    """
    record_data = raw_record_data
    debug("update_record(%(field_list)s, %(record_data)s)" % locals())


    record_data_dict = record_data
    database_query = field_list

    cli_query_list = get_query_fields(field_list)
    database_query = generate_database_multi_query(cli_query_list)

    if isinstance(record_data, dict) and '$set' not in record_data.keys():
        record_data_list = []
        for key, value in record_data.items():
            if type(value).__name__ == 'list':
                record_data_list.append("%s=%s" % (key, ",".join(value)))
                continue
            record_data_list.append("%(key)s=%(value)s" % locals())
        record_data = " ".join(record_data_list)

    record_data_list = get_query_fields(record_data)
    #record_data_dict = generate_database_multi_update(record_data_list)
    record_data_dict = {'$set': raw_record_data}

    debug("update_record: record_data_dict=%(record_data_dict)s "
          "database_query=%(database_query)s" % locals())

    rc = db.RecordKeeper()
    rc.update(database_query, record_data_dict)


def saved_queries_list():
    """ Return a list of saved queries. """
    rc = db.RecordKeeper()
    query_list = rc.saved_queries_list()
    return query_list


def saved_queries_add(query_name, query_data=None):
    """ Add a new saved query. """
    rc = db.RecordKeeper()
    rc.saved_queries_add(query_name=query_name, query_data=query_data)


def saved_queries_get(query_name):
    """ get a saved query. """
    rc = db.RecordKeeper()
    query_data = rc.saved_queries_get(query_name=query_name)
    return query_data


def extract_names_from_records(record_list):
    """ Given a list of records, return a list() of names of the records. """
    if type(record_list).__name__ in ["str", "unicode"]:
        record_list = find_records(record_list)

    name_list = []
    for record in record_list:
        name_list.append(record['name'])

    return name_list


def relate_records(query_one, query_two, link="parent"):
    """ relate 2 groups of records to each other via a defined link.
    The 2 queries ( query_one and query_two ), will be expanded, then all the
    records matching the 2 queries will be related via the link.
    """

    query_two_records = find_records(query_two)
    debug("-")

    link_key = "link_%(link)s" % locals()
    name_list = extract_names_from_records(query_two_records)
    relationship = {link_key: name_list}

    debug("relate_records->update_record(%(query_one)s, %(relationship)s)" % locals())

    update_results = update_record(query_one, relationship)

    return update_results

def list_keys():
    rc = db.RecordKeeper()
    keys = rc.list_keys()
    return keys

