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

KNOWN_PROTCOLS = {
    '-1': '',
    '1': 'ICMP',
    '6': 'TCP',
    '17': 'UDP'
}


def import_nrtb_aws_cli():
    start = time.time()

    raw_rtb = os.popen("aws ec2 describe-route-tables").read()
    rtb_list = json.loads(raw_rtb)['RouteTables']

    stats = {'added': 0, 'failed': 0}
    for r in rtb_list:
        rtb_raw = r
        rtb = {}

        if 'Tags' in rtb_raw:
            tags = {}
            for t in rtb_raw['Tags']:
                k = t['Key']
                v = t['Value']
                tags[k] = v
            rtb_raw.update(tags)

        # pprint(rtb_raw)

        rtb['name'] = rtb_raw['RouteTableId']
        rtb['_type'] = 'rtb'

        for key, value in rtb_raw.items():
            key = key.lower()
            if isinstance(value, str) or isinstance(value, unicode):
                rtb[key] = value
                continue
            if isinstance(value, int) or isinstance(value, bool):
                rtb[key] = value
                continue

            if key == "tags":
                rtb['tags'] = []
                for t in value:
                    k = t['Key'].lower()
                    v = t['Value']
                    rtb['tag_%s' % k] = v
                    rtb['tags'].append(k)
                continue

            if key == "associations":
                rtb['subnetid'] = []
                for acc in value:
                    if 'SubnetId' in acc:
                        rtb['subnetid'].append(acc['SubnetId'])
                continue

            if key == "routes":
                rtb['routes'] = []
                for r in value:
                    if r['State'] != 'active':
                        continue
                    v = None
                    if 'GatewayId' in r:
                        v = "%s %s" % (
                            r['DestinationCidrBlock'], r['GatewayId'])
                    else:
                        v = "%s %s" % (
                            r['DestinationCidrBlock'], r['InstanceId'])
                    rtb['routes'].append(v)
                continue

            if not value:
                continue

            print key, pprint(value)
            print

        for bad_name, good_name in PRETTY_NAMES.items():
            rtb[good_name] = rtb[bad_name]

        # pprint(rtb)

        try:
            recordkeeper.api.insert_record(rtb)
            stats['added'] += 1
        except recordkeeper.rc_exceptions.DuplicateRecord as error:
            stats['failed'] += 1
            print error

    finished = time.time()

    print stats, finished - start

if __name__ == '__main__':
    import_nrtb_aws_cli()
