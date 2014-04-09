#!/usr/bin/env python
import time
import json
import os

import recordkeeper.api
import recordkeeper.rc_exceptions
import recordkeeper.settings

recordkeeper.settings.DEBUG = True

PRETTY_NAMES = {
    'vpcid': 'vpc',
    'privateipaddress': 'ip',
    'instanceid': 'instances'
}


def import_ec2_aws_cli():
    start = time.time()

    raw_ec2 = os.popen("aws ec2 describe-instances").read()
    ec2_list = json.loads(raw_ec2)['Reservations']

    stats = {'added': 0, 'failed': 0}
    for r in ec2_list:
        ec2_raw = r['Instances'][0]
        ec2 = {}

        tags = {}
        for t in ec2_raw['Tags']:
            k = t['Key']
            v = t['Value']
            tags[k] = v
        ec2_raw.update(tags)

        ec2['name'] = ec2_raw['Name']
        ec2['_type'] = 'ec2'

        for key, value in ec2_raw.items():
            key = key.lower()
            if isinstance(value, str) or isinstance(value, unicode):
                ec2[key] = value
                continue
            if isinstance(value, int) or isinstance(value, bool):
                ec2[key] = value
                continue

            if key == "securitygroups":
                ec2["securitygroups"] = []
                ec2["securitygroups_ids"] = []
                for sg in value:
                    sg_name = sg['GroupName']
                    sg_id = sg['GroupId']
                    ec2["securitygroups"].append(sg_name)
                    ec2["securitygroups_ids"].append(sg_id)
                continue

            if key == "tags":
                print value
                ec2['tags'] = []
                for t in value:
                    k = t['Key'].lower()
                    v = t['Value']
                    ec2['tag_%s' % k] = v
                    ec2['tags'].append(k)
                continue

            if key == "blockdevicemappings":
                ec2['block_devices'] = []
                ec2['ebs_volumes'] = []
                for d in value:
                    ec2['block_devices'].append(d['DeviceName'])
                    ec2['ebs_volumes'].append(d['Ebs']['VolumeId'])

                continue

            if key == "placement":
                ec2['availabilityzone'] = value['AvailabilityZone']
                continue

            #print key, pprint(value)

        for bad_name, good_name in PRETTY_NAMES.items():
            ec2[good_name] = ec2[bad_name]

        try:
            recordkeeper.api.insert_record(ec2)
            stats['added'] += 1
        except recordkeeper.rc_exceptions.DuplicateRecord as error:
            stats['failed'] += 1
            print error

    finished = time.time()

    print stats, finished - start

if __name__ == '__main__':
    import_ec2_aws_cli()
