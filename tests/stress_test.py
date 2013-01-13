#!/usr/bin/env python
import cli
import time
import settings

settings.DEBUG = False
#
def add(NUMBER_OR_RECORDS_TO_ADD):
	start = time.time()
	for counter in range(0,NUMBER_OR_RECORDS_TO_ADD):
		record_data = "name=item%(counter)d a=1 b=2 c=3 d=4 e=5 f=6" % locals()
		cli.cli_add_record(record_data)
	finish = time.time()	
	print "add: took %.5f seconds, to add %s" % ( finish - start, NUMBER_OR_RECORDS_TO_ADD )
	print "add: thats %.8f seconds per record" % ( ( finish - start) / NUMBER_OR_RECORDS_TO_ADD )


def delete_all_at_once():
	start = time.time()
	cli.cli_delete_record("name.defined")
	finish = time.time()	
	print "delete_all_at_once: took %.5f seconds" % ( finish - start)


def delete_all_one_by_one(NUMBER_OR_RECORDS_TO_ADD):
	start = time.time()
	for counter in range(0,NUMBER_OR_RECORDS_TO_ADD):
		record_data = "name=item%(counter)d" % locals()
		cli.cli_delete_record(record_data)
	finish = time.time()	
	print "delete_all_one_by_one: took %.5f seconds, to add %s" % ( finish - start, NUMBER_OR_RECORDS_TO_ADD )
	print "delete_all_one_by_one: thats %.8f seconds per record" % ( ( finish - start) / NUMBER_OR_RECORDS_TO_ADD )



delete_all_at_once()
add(10)
delete_all_at_once()

delete_all_at_once()
add(100)
delete_all_at_once()

delete_all_at_once()
add(1000)
delete_all_at_once()
