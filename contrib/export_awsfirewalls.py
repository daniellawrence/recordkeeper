#!/usr/bin/env python
from recordkeeper.api import find_records
import sys

WITH_ROUTE_INFO = False

rk_filter = ""

if len(sys.argv) > 1:
    rk_filter = ' '.join(sys.argv[1:])

for instance in find_records("_type=instances %s" % rk_filter):
    # Security group lookup
    sg_ids = ','.join(instance['securitygroups_ids'])
    find_sg = "_type=securitygroups securitygroups_ids.in.%s" % sg_ids
    sg = find_records(find_sg)

    # subnet lookup
    sn_ids = instance['subnets']
    find_sn = "_type=subnets subnets.in.%s" % sn_ids
    sn = find_records(find_sn)

    # nacl lookup
    find_nacl = "_type=acls subnetid.in.%s" % sn_ids
    nacl = find_records(find_nacl)

    # RouteTable lookup
    find_rtb = "_type=rtb subnetid.in.%s" % sn_ids
    try:
        rtb = find_records(find_rtb)
    except Exception:
        rtb = []

    print "instance:", instance['name'], "id:", instance['instances']
    print "=" * 80

    print
    print "-" * 80
    print "Routes"
    print "-" * 80
    for r in rtb:
        for route in r['routes']:
            print "ROUTE", route, " rtb:", r['name']

    print
    print "-" * 80
    print "Network Access Control Lists"
    print "-" * 80
    #
    for i in nacl:
        for r in i['ingress']:
            print "INGRESS", r, "nacl:", i['name']
        for r in i['egress']:
            print "ENGRESS", r, "nacl:", i['name']

    print
    print "-" * 80
    print "Security Groups"
    print "-" * 80

    for i in sg:
        if len(i['ingress']) + len(i['egress']) == 0:
            continue
        print i['description']
        for r in i['ingress']:
            print "INGRESS", r, "security_group:", i['name']
        for r in i['egress']:
            print "EGRESS", r, "security_group:", i['name']
        print

    print
    print
