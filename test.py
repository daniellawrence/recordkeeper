#!/usr/bin/env python
import db
import cli

recordkeeper = db.RecordKeeper()
print recordkeeper.records



print "="*80
print 'cli_print_record("name name=john age>30")'
print "-"*80
cli.cli_print_record("name name=john age>30")
print "="*80
