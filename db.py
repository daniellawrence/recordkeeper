#!/usr/bin/env python

import pymongo
import settings


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


    def find(self, database_query, display_fields = None):
        """ Search the database with the database_query and only return the
        fields that match the display_fields.
        TODO: Work out if there is any benefit of reducing the fields that are
              getting returned.
        """
        print "db.find: %(database_query)s" % locals()

        result_set = None
        if display_fields:
            result_set = self.records.find(database_query, fields = display_fields)
        else:
            result_set = self.records.find(database_query)

        # If database_query finds not results, then generate an exception
        if result_set.count() == 0:
            raise Exception("No records found")

        return result_set

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

        # name is the unique key that is used across the.
        record_name = record_data['name']
        unique_query = {'name': record_name}

        # Check to see if we already have this record in the database
        existing_record = self.find_one(unique_query)
        if existing_record:
            print "Failing to add duplicate record: %(record_data)s" %  locals()
            return existing_record

        # If it is a brand new record, save it to the database.
        # Then return the newly created record to the user.
        new_record = self.records.insert( record_data )
        return new_record


    def remove_by_id(self, query_id):
        """ Search the database for a single record that matches the provided
        id 100%.
        Once the record is found delete it.
        """
        print "db.remove_by_id: %(query_id)s" % locals()
        self.records.remove( query_id )

        return True

    def remove(self, database_query):
        """ Search the database for records that match the database_query once
        the records are found, delete them.
        """
        print "db.remove: %(database_query)s" % locals()
        self.records.remove( database_query )

        return True

    def update(self, database_query, record_data):
        """ Query the database using database_query, then update all the keys
        where record_data has some new data.
        """
        print  "db.update: %(database_query)s with %(record_data)s" % locals()
        database_results = self.records.update( database_query, record_data, multi=True)
        return database_results
