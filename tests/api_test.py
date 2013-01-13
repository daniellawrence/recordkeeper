#!/usr/bin/env python
import api
from rc_exceptions import DuplicateRecord, NoRecordsFound
import time


start = time.time()

record_data = {'name': 'danny', 'age': 54}
try:
	api.insert_record( record_data )
except DuplicateRecord as error:
	print "%(error)s" % locals()
	

database_record = api.find_records({'name': 'danny'})
api.delete_record( {'name': 'danny'} )

finish = time.time()

time_taken = finish - start

print "Added then deleted: %(database_record)s, in %(time_taken)5f seconds" % locals()