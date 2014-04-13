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


def import_sg_aws_cli():
    start = time.time()

    raw_sg = os.popen("aws ec2 describe-security-groups").read()
    sg_list = json.loads(raw_sg)['SecurityGroups']

    stats = {'added': 0, 'failed': 0}
    for r in sg_list:
        sg_raw = r
        sg = {}

        if 'Tags' in sg_raw:
            tags = {}
            for t in sg_raw['Tags']:
                k = t['Key']
                v = t['Value']
                tags[k] = v
            sg_raw.update(tags)

        sg['name'] = sg_raw['GroupName']
        sg['_type'] = 'securitygroups'
        sg['securitygroups_ids'] = [sg_raw['GroupId']]

        for key, value in sg_raw.items():
            key = key.lower()
            if isinstance(value, str) or isinstance(value, unicode):
                sg[key] = value
                continue
            if isinstance(value, int) or isinstance(value, bool):
                sg[key] = value
                continue

            if key == "securitygroups":
                sg["securitygroups"] = []
                sg["securitygroups_ids"] = []
                for sg in value:
                    sg_name = sg['GroupName']
                    sg_id = sg['GroupId']
                    sg["securitygroups"].append(sg_name)
                    sg["securitygroups_ids"].append(sg_id)
                continue

            if key == "tags":
                sg['tags'] = []
                for t in value:
                    k = t['Key'].lower()
                    v = t['Value']
                    sg['tag_%s' % k] = v
                    sg['tags'].append(k)
                continue

            if key == "ippermissionsegress":
                sg['egress'] = []
                for r in value:
                    if 'ToPort' not in r:
                        continue
                    for ipr in r['IpRanges']:
                        rule = "%s:%s" % (ipr['CidrIp'], r['ToPort'])
                        sg['egress'].append(rule)

                    for sub_sg in r['UserIdGroupPairs']:
                        sub_gid = sub_sg['GroupId']
                        sg['securitygroups_ids'] = sub_gid

                        rule = "%s:%s" % (sub_gid, r['ToPort'])
                        sg['egress'].append(rule)

                continue

            if key == "ippermissions":
                sg['ingress'] = []
                for r in value:
                    if 'ToPort' not in r:
                        continue
                    for ipr in r['IpRanges']:
                        rule = "%s:%s" % (ipr['CidrIp'], r['ToPort'])
                        sg['ingress'].append(rule)

                    for sub_sg in r['UserIdGroupPairs']:
                        sub_gid = sub_sg['GroupId']
                        sg['securitygroups_ids'] = sub_gid

                        rule = "%s:%s" % (sub_gid, r['ToPort'])
                        sg['ingress'].append(rule)

                continue

            if key == "placement":
                sg['availabilityzone'] = value['AvailabilityZone']
                continue

            print key, pprint(value)

        for bad_name, good_name in PRETTY_NAMES.items():
            sg[good_name] = sg[bad_name]

        try:
            recordkeeper.api.insert_record(sg)
            stats['added'] += 1
        except recordkeeper.rc_exceptions.DuplicateRecord as error:
            stats['failed'] += 1
            print error

    finished = time.time()

    print stats, finished - start

if __name__ == '__main__':
    import_sg_aws_cli()
