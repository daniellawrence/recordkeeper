#!/usr/bin/env python
import time
import json
import os
from pprint import pprint

import recordkeeper.api
import recordkeeper.rc_exceptions
import recordkeeper.settings

recordkeeper.settings.DEBUG = False

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

        sg['description'] = sg_raw['GroupName']
        sg['_type'] = 'securitygroups'
        sg['securitygroups_ids'] = [sg_raw['GroupId']]
        sg['name'] = sg_raw['GroupId']

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
                sg['egress_allow'] = []
                sg['egress'] = []
                for r in value:

                    if 'ToPort' not in r:
                        continue

                    for ipr in r['IpRanges']:
                        rule = "%s:%s" % (ipr['CidrIp'], r['ToPort'])
                        sg['egress_allow'].append(rule)
                        sg['egress'].append("ALLOW 0 %s" % rule)

                    for sub_sg in r['UserIdGroupPairs']:
                        sub_gid = sub_sg['GroupId']
                        sg['securitygroups_ids'] = sub_gid

                        rule = "%s:%s" % (sub_gid, r['ToPort'])
                        #sg['egress_allow'].append(rule)
                        #sg['egress'].append("ALLOW 0 %s" % rule)

                        find_query = "_type.not.securitygroups securitygroups_ids=%s" % sub_gid
                        #find_query = "securitygroups_ids=%s" % sub_gid
                        try:
                            items_in_sg = recordkeeper.api.find_records(find_query)
                        except Exception:
                            print sg['name'], "WARNING!: no matches for", sub_sg
                            continue
                            pass

                        for item in items_in_sg:
                            rule = "%s/32:%s" % (item['ip'], port)
                            sg['egress_allow'].append(rule)
                            sg['egress'].append("ALLOW 0 %s" % rule)

                continue

            if key == "ippermissions":
                sg['ingress'] = []
                sg['ingress_allow'] = []
                sg['ingress'] = []
                for r in value:
                    rn = 0
                    if 'ToPort' not in r:
                        continue

                    port = ''
                    if r['ToPort'] == r['FromPort']:
                        port =  '%s/%s' % (r['ToPort'], r['IpProtocol'].upper())
                    else:
                        port = '%s-%s/%s' % (r['ToPort'], r['FromPort'], r['IpProtocol'].upper())

                    for ipr in r['IpRanges']:
                        rule = "%s %s:%s" % (rn, ipr['CidrIp'], port) 
                        #sg['ingress_allow'].append(rule)
                        #sg['ingress'].append("ALLOW %s" % rule)

                    for sub_sg in r['UserIdGroupPairs']:
                        sub_gid = sub_sg['GroupId']
                        sg['securitygroups_ids'] = sub_gid

                        find_query = "_type.not.securitygroups securitygroups_ids=%s" % sub_gid
                        #find_query = "securitygroups_ids=%s" % sub_gid
                        try:
                            items_in_sg = recordkeeper.api.find_records(find_query)
                        except Exception:
                            print sg['name'], "WARNING!, no matches for", sub_sg
                            print "rk_print name _type", find_query
                            continue
                            pass

                        for item in items_in_sg:
                            rule = "%s/32:%s" % (item['ip'], port)
                            sg['ingress_allow'].append(rule)
                            sg['ingress'].append("0 ALLOW %s" % rule)

                continue

            if key == "placement":
                sg['availabilityzone'] = value['AvailabilityZone']
                continue

            #print key, pprint(value)

        for bad_name, good_name in PRETTY_NAMES.items():
            sg[good_name] = sg[bad_name]

        sg['name'] = sg['groupid']
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
