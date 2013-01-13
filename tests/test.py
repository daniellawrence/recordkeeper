#!/usr/bin/env python
from recordkeeper import settings
settings.DEBUG = True
from recordkeeper import cli
import time
#

start = time.time()
cli.cli_delete_record("name.defined")
cli.cli_add_record("name=john age=31 sex=male")
#cli.cli_add_record("name=jeff age=52 sex=male")
#cli.cli_add_record("name=fred age=29 sex=male")
#cli.cli_add_record("name=sandy age=22 sex=female")
#cli.cli_add_record("name=bob age=31 sex=male")
#cli.cli_add_record("name=greg age=52 sex=male")
#cli.cli_add_record("name=dan age=29 sex=male")
#cli.cli_add_record("name=sam age=22 sex=female")

#cli.cli_delete_record("age>30")
#cli.cli_update_record("name=fred","age=0")
#cli.cli_print_record("name.defined name age sex")
#cli.cli_delete_record("age<1")
cli.cli_print_record({'age': '31'})

finish = time.time()

print "took %.5f seconds" % ( finish - start )

