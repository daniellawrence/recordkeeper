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
}


def import_elb_aws_cli():
    start = time.time()

    raw_elb = os.popen("aws elb describe-load-balancers").read()
    elb_list = json.loads(raw_elb)['LoadBalancerDescriptions']

    stats = {'added': 0, 'failed': 0}
    for r in elb_list:
        elb_raw = r
        elb = {}

        elb['name'] = elb_raw['LoadBalancerName']
        elb['_type'] = 'elb'

        for key, value in elb_raw.items():
            key = key.lower()
            if isinstance(value, str) or isinstance(value, unicode):
                elb[key] = value
                continue
            if isinstance(value, int) or isinstance(value, bool):
                elb[key] = value
                continue

            if key == "securitygroups":
                elb['securitygroups'] = value
                continue

            if key == "blockdevicemappings":
                elb['block_devices'] = []
                elb['ebs_volumes'] = []
                for d in value:
                    elb['block_devices'].append(d['DeviceName'])
                    elb['ebs_volumes'].append(d['Ebs']['VolumeId'])
                continue

            if key == "placement":
                elb['availabilityzone'] = value['AvailabilityZone']
                continue
                
            if key == "subnets":
                elb['subnets'] = value
                continue

            if key == "instances":
                elb['instances'] = []
                for d in value:
                    elb['instances'].append(d['InstanceId'])
                continue

            if key == "sourcesecuritygroup":
                elb['sorcesecuritygroup'] = value['GroupName']
                continue

            if key == "availabilityzones":
                elb['availabilityzones'] = value
                continue

            print key, pprint(value)
        print "-"

        for bad_name, good_name in PRETTY_NAMES.items():
            elb[good_name] = elb[bad_name]

        try:
            recordkeeper.api.insert_record(elb)
            stats['added'] += 1
        except recordkeeper.rc_exceptions.DuplicateRecord as error:
            stats['failed'] += 1
            print error

    finished = time.time()

    print stats, finished - start

if __name__ == '__main__':
    import_elb_aws_cli()
