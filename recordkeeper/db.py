#!/usr/bin/env python

import pymongo
import settings
from rc_exceptions import DuplicateRecord, NoRecordsFound, InvaildQuery, \
                          MissingRequiredInformaton, RequiredField

def debug(msg):
    """ print a debug message. """
    if settings.DEBUG:
        print "DEBUG: db.%(msg)s" % locals()
    pass

#------------------------------------------------------------------------------
class RecordKeeper():
    """  
    Main recordkeeper instance, once created it is able to CRUD the mongodb
    """

    # localhost of the mongodb server
    DATABASE_HOST = settings.DATABASE_HOST
    # port of the mongodb service
    DATABASE_PORT = settings.DATABASE_PORT
    # database that we will be playing with
    DATABASE_NAME = settings.DATABASE_NAME

    #---------------------------------------------------------------------------
    def __init__(self):
        """
        Create a new database connection and records table that will be used
        """
        self.conn = pymongo.Connection( self.DATABASE_HOST, self.DATABASE_PORT)
        self.database = self.conn[ self.DATABASE_NAME ]
        self.records = self.database.records
        self.records.ensure_index( 'name', unique=True)
        self.database.saved_queries.ensure_index( 'name', unique=True)

    def saved_queries_list(self):
        """ Return a list of saved queries. """
        saved_queries = self.database.saved_queries.find({})
        if saved_queries.count() == 0:
            raise NoRecordsFound("No queries found")

        return saved_queries

    def saved_queries_add(self, query_name, query_data=None):
        """ Return a list of saved queries. """
        self.database.saved_queries.insert(
            {
                'name': query_name,
                'query_data': query_data
            }
        )

    def saved_queries_get(self, query_name):
        """ Return a saved_queries, "query_data". """
        saved_query = self.database.saved_queries.find({'name': query_name})
        if saved_query.count() == 0:
            raise NoRecordsFound("saved query '%(query_name)s' not found in database" % locals())


        query_data = saved_query[0]['query_data']
        return query_data

    def saved_queries_remove(self, query_name):
        """ Return a saved_queries, "query_data". """
        self.database.saved_queries.remove({'name': query_name})

    def list_keys(self):
        """ List all the keys used. """
        from bson.code import Code
        map_code = Code("""
        function () {
            for (var key in this) 
            {
                emit(key, null);
            }
        }
        """)
        reduce_code = Code("""
        function(key, stuff) { 
            return null;
        }
        """)
        self.records.map_reduce(map_code, reduce_code, "unique_keys")
        unique_keys = list(self.database.unique_keys.find().distinct("_id"))
        return unique_keys

    def find(self, database_query, display_fields = None):
        """ Search the database with the database_query and only return the
        fields that match the display_fields.
        TODO: Work out if there is any benefit of reducing the fields that are
              getting returned.
        """
        debug("find: %(database_query)s" % locals())

        if database_query == None:
            raise InvaildQuery("Missing database query: %(database_query)s" % locals())

        result_set = None
        if display_fields:
            debug("find.records.find( %(database_query)s, fields=%(display_fields)s)" % locals())
            result_set = self.records.find(database_query, fields = display_fields)
        else:
            debug("find.records.find( %(database_query)s ) " % locals())
            result_set = self.records.find(database_query)

        # If database_query finds not results, then generate an exception
        if result_set.count() == 0:
            raise NoRecordsFound("No records found: %(database_query)s" % locals())

        return list(result_set)

    def find_one_by_id(self, query_id):
        """ Search the database for a single record that matches the provided
        id 100%.
        """
        # Convert the unicode query_id into a bson objectid for searching
        #object_id = bson.objectid.ObjectId(query_id)
        return self.records.find_one( query_id )

    def find_one( self, database_query, display_fields = None):
        """ Search the database for a single record that matches the provide
        database_query.
        """
        result_set = self.records.find_one(database_query, fields = display_fields)
        return result_set


    def insert(self, record_data):
        """ This will take a python dict() record_data and save it to the 
        database.
        """

        debug("insert: record_data=%(record_data)s" % locals())

        if not record_data:
            raise MissingRequiredInformaton("Missing record_data")


        # name is the only required field.
        record_name = None
        record_type = None
        try:
            record_name = record_data['name']
        except KeyError:
            raise MissingRequiredInformaton("record_data is missing required field 'name'")

        if '_type' in record_data:
            record_type = record_data['_type']
        else:
            record_type = '_record'

        # name is the unique key that is used across the.
        unique_query = {'name': record_name, '_type': record_type}


        for key, value in record_data.items():
            try:
                if ',' in value:
                    record_data[key] = value.split(',')
                if isinstance(value, list):
                    continue
                if isinstance(value, set):
                    record_data[key] = list(value)
                    continue
            except TypeError:
                continue

            if value.isdigit():
                record_data[key] = float(value)


        debug("insert: %(record_data)s" % locals())

        # Check to see if we already have this record in the database
        existing_record = self.find_one(unique_query)
        if existing_record:
            raise DuplicateRecord(
                "Failed to add duplicate record: %s %s - %s" % (
                    record_data['name'], record_data['_type'], record_data
                )
            )

        # If it is a brand new record, save it to the database.
        # Then return the newly created record to the user.
        new_record = self.records.insert( record_data )
        return new_record


    def remove_by_id(self, query_id):
        """ Search the database for a single record that matches the provided
        id 100%.
        Once the record is found delete it.
        """
        #print "db.remove_by_id: %(query_id)s" % locals()
        self.records.remove( query_id )

        return True

    def remove(self, database_query, force=False):
        """ Search the database for records that match the database_query once
        the records are found, delete them.
        """
        debug("remove: %(database_query)s" % locals())
        if not force:
            self.find(database_query)
        self.records.remove(database_query)

        return True

    def update(self, database_query, record_data):
        """ Query the database using database_query, then update all the keys
        where record_data has some new data.
        """
        debug("update(%s)" % locals())
        if not record_data:
            raise RequiredField("Missing record_data, unable to update records.")

        database_results = self.records.update(database_query, record_data,
            multi = True)

        

        return database_results
