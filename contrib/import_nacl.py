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


def import_nacl_aws_cli():
    start = time.time()

    raw_acl = os.popen("aws ec2 describe-network-acls").read()
    acl_list = json.loads(raw_acl)['NetworkAcls']

    stats = {'added': 0, 'failed': 0}
    for r in acl_list:
        acl_raw = r
        acl = {}

        if 'Tags' in acl_raw:
            tags = {}
            for t in acl_raw['Tags']:
                k = t['Key']
                v = t['Value']
                tags[k] = v
            acl_raw.update(tags)

        acl['name'] = acl_raw['NetworkAclId']
        acl['_type'] = 'acls'
        acl['acls_ids'] = [acl_raw['NetworkAclId']]
        acl['acls'] = [acl_raw['NetworkAclId']]

        for key, value in acl_raw.items():
            key = key.lower()
            if isinstance(value, str) or isinstance(value, unicode):
                acl[key] = value
                continue
            if isinstance(value, int) or isinstance(value, bool):
                acl[key] = value
                continue

            if key == "tags":
                acl['tags'] = []
                for t in value:
                    k = t['Key'].lower()
                    v = t['Value']
                    acl['tag_%s' % k] = v
                    acl['tags'].append(k)
                continue

            if key == "entries":
                acl['egress'] = []
                acl['egress_allow'] = []
                acl['egress_deny'] = []
                #
                acl['ingress'] = []
                acl['ingress_allow'] = []
                acl['ingress_deny'] = []

                for rule in value:
                    rn = rule['RuleNumber']
                    v = '%s %s' % (rn, rule['CidrBlock'])
                    if 'PortRange' in rule:
                        pr = rule['PortRange']
                        p = KNOWN_PROTCOLS[rule['Protocol']]
                        if pr['To'] == pr['From']:
                            v = '%s %s:%s/%s' % (rn,
                                                 rule['CidrBlock'], pr['To'], p)
                        else:
                            v = '%s %s:%s-%s/%s' % (rn,
                                                    rule['CidrBlock'], pr['To'], pr['From'], p)

                    if rule['Egress']:
                        if rule['RuleAction'] == 'allow':
                            acl['egress_allow'].append(v)
                            acl['egress'].append('ALLOW %s' % v)
                        else:
                            acl['egress_deny'].append(v)
                            acl['egress'].append('ALLOW %s' % v)
                    else:
                        if rule['RuleAction'] == 'allow':
                            acl['ingress_allow'].append(v)
                            acl['ingress'].append('ALLOW %s' % v)
                        else:
                            acl['ingress_deny'].append(v)
                            acl['ingress'].append('DENY %s' % v)
                    continue

            if key == "associations":
                acl['subnetid'] = []
                if not value:
                    continue
                print
                print
                for acc in value:
                    print acc
                    acl['subnetid'].append(acc['SubnetId'])

            print key, pprint(value)
            print

        for bad_name, good_name in PRETTY_NAMES.items():
            acl[good_name] = acl[bad_name]

        try:
            recordkeeper.api.insert_record(acl)
            stats['added'] += 1
        except recordkeeper.rc_exceptions.DuplicateRecord as error:
            stats['failed'] += 1
            print error

    finished = time.time()

    print stats, finished - start

if __name__ == '__main__':
    import_nacl_aws_cli()
