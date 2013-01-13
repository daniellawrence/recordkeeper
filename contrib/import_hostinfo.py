#!/usr/bin/env python
import csv
import api
import rc_exceptions
import time
import settings

settings.DEBUG = False
def import_hostinfo_csv(filename):
    start = time.time()
    f = open(filename)
    reader = csv.DictReader(f)

    stats = {'added': 0, 'failed': 0}
    for row in reader:

        row['name'] = row['hostname']
        row['_type'] = row['type']

        #url_add = []
        #for key, value in row.items():
        #    if value:
        #        url_add.append( "%(key)s='%(value)s'" % locals())
        #print "http://localhost:5000/json/add_record/%s" % " ".join( url_add)

        try:
            api.insert_record( row )
            stats['added'] += 1
        except rc_exceptions.DuplicateRecord as error:
            stats['failed'] += 1

    finished = time.time()

    print stats, finished - start, filename

import_hostinfo_csv("/home/dannyla/Dropbox/RecordKeeperProject/raw/hostinfo_linux.txt")
import_hostinfo_csv("/home/dannyla/Dropbox/RecordKeeperProject/raw/hostinfo_solaris.txt")
import_hostinfo_csv("/home/dannyla/Dropbox/RecordKeeperProject/raw/hostinfo_windows.txt")

