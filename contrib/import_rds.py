#!/usr/bin/env python
import time
import json
import os
from pprint import pprint

import recordkeeper.api
import recordkeeper.rc_exceptions
import recordkeeper.settings

recordkeeper.settings.DEBUG = True

PRETTY_NAMES = {
    'engineversion': 'version',
    'subnetid': 'subnets'
}


def import_rds_aws_cli():
    start = time.time()

    raw_rds = os.popen("aws rds describe-db-instances").read()
    rds_list = json.loads(raw_rds)['DBInstances']

    stats = {'added': 0, 'failed': 0}
    for r in rds_list:
        rds_raw = r
        rds = {}

        rds['name'] = rds_raw['DBInstanceIdentifier']
        rds['_type'] = 'rds'
        

        for key, value in rds_raw.items():
            key = key.lower()
            if isinstance(value, str) or isinstance(value, unicode):
                rds[key] = value
                continue
            if isinstance(value, int) or isinstance(value, bool):
                rds[key] = value
                continue

            if key == "vpcsecuritygroups":
                rds['securitygroups_ids'] = []
                for g in value:
                    rds['securitygroups_ids'].append(g['VpcSecurityGroupId'])
                continue

            if key == "optiongroupmemberships":
                rds['option_groups'] = []
                for d in value:
                    rds['option_groups'].append(d['OptionGroupName'])
                continue

            if key == "dbparametergroups":
                rds['parameter_groups'] = []
                for d in value:
                    rds['parameter_groups'].append(d['DBParameterGroupName'])
                continue

            if key == "dbsubnetgroup":
                rds['subnetid'] = []
                for sn in value['Subnets']:
                    rds['subnetid'].append(sn['SubnetIdentifier'])
                continue
                
            if key == "endpoint":
                rds['endpoint'] = "%s:%s" % (value['Address'], value['Port'])
                continue

            if key == "instances":
                rds['instances'] = []
                for d in value:
                    rds['instances'].append(d['InstanceId'])
                continue

            if key == "sourcesecuritygroup":
                rds['sorcesecuritygroup'] = value['GroupName']
                continue

            if key == "availabilityzones":
                rds['availabilityzones'] = value
                continue

            #print key, pprint(value)
        #print "-"

        for bad_name, good_name in PRETTY_NAMES.items():
            rds[good_name] = rds[bad_name]

        try:
            recordkeeper.api.insert_record(rds)
            stats['added'] += 1
        except recordkeeper.rc_exceptions.DuplicateRecord as error:
            stats['failed'] += 1
            print error

    finished = time.time()

    print stats, finished - start

if __name__ == '__main__':
    import_rds_aws_cli()
