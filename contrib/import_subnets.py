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
    'vpcid': 'vpc',
}


def import_sn_aws_cli():
    start = time.time()

    raw_sn = os.popen("aws ec2 describe-subnets").read()
    sn_list = json.loads(raw_sn)['Subnets']

    stats = {'added': 0, 'failed': 0}
    for r in sn_list:
        sn_raw = r
        sn = {}

        if 'Tags' in sn_raw:
            tags = {}
            for t in sn_raw['Tags']:
                k = t['Key']
                v = t['Value']
                tags[k] = v
            sn_raw.update(tags)

        sn['name'] = sn_raw['SubnetId']
        sn['_type'] = 'sn'
        sn['subnets'] = [sn_raw['SubnetId']]

        for key, value in sn_raw.items():
            key = key.lower()
            if isinstance(value, str) or isinstance(value, unicode):
                sn[key] = value
                continue
            if isinstance(value, int) or isinstance(value, bool):
                sn[key] = value
                continue

            if key == "securitygroups":
                sn["securitygroups"] = []
                sn["securitygroups_ids"] = []
                for sn in value:
                    sn_name = sn['GroupName']
                    sn_id = sn['GroupId']
                    sn["securitygroups"].append(sn_name)
                    sn["securitygroups_ids"].append(sn_id)
                continue

            if key == "tags":
                sn['tags'] = []
                for t in value:
                    k = t['Key'].lower()
                    v = t['Value']
                    sn['tag_%s' % k] = v
                    sn['tags'].append(k)
                continue

            if key == "placement":
                sn['availabilityzone'] = value['AvailabilityZone']
                continue

            print key, pprint(value)

        for bad_name, good_name in PRETTY_NAMES.items():
            sn[good_name] = sn[bad_name]

        try:
            recordkeeper.api.insert_record(sn)
            stats['added'] += 1
        except recordkeeper.rc_exceptions.DuplicateRecord as error:
            stats['failed'] += 1
            print error

    finished = time.time()

    print stats, finished - start

if __name__ == '__main__':
    import_sn_aws_cli()
