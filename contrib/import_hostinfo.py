#!/usr/bin/env python
import csv
import time
import sys

import recordkeeper.api
import recordkeeper.rc_exceptions
import recordkeeper.settings

recordkeeper.settings.DEBUG = False


def import_hostinfo_csv(filename):
    start = time.time()
    f = open(filename)
    reader = csv.DictReader(f)

    stats = {'added': 0, 'failed': 0}
    for row in reader:

        row['name'] = row['hostname']
        row['_type'] = row['type']

        try:
            recordkeeper.api.insert_record(row)
            stats['added'] += 1
        except recordkeeper.rc_exceptions.DuplicateRecord:
            stats['failed'] += 1

    finished = time.time()

    print stats, finished - start, filename

if __name__ == '__main__':
    import_hostinfo_csv(sys.argv[1])
