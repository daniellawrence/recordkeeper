#!/usr/bin/env python
from recordkeeper.api import find_records
from netaddr import IPNetwork, IPAddress
import sys

WITH_ROUTE_INFO = False

rk_filter = ""

if len(sys.argv) > 1:
    rk_filter = ' '.join(sys.argv[1:])


def instance2rtb(instance):
    sn_ids = instance['subnets']
    find_sn = "_type=subnets subnets.in.%s" % sn_ids
    # RouteTable lookup
    find_rtb = "_type=rtb subnetid.in.%s" % sn_ids
    try:
        rtb = find_records(find_rtb)
    except Exception:
        rtb = []
    return rtb


def show_routes(rtb, step=0, target_filter=None):
    for r in rtb:
        r_name = r['routetableid']
        for route in r['routes']:
            (target, destination) = route.split()
            if target_filter:
                if IPAddress(target.split('/')[0]) not in IPNetwork(target_filter):
                    continue
            print ' '*step, route, " rtb:", r['name'], r_name
            if destination.startswith('i-'):
                destination = destination.replace('i-', '')
                instance = find_records("_type=instances instances~%s" % destination)[0]
                local_rtb = instance2rtb(instance)
                show_routes(local_rtb, step+3, target)


for instance in find_records("_type=instances %s" % rk_filter):
    print
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
    show_routes(rtb)

    print
    print "-" * 80
    print "Network Access Control Lists"
    print "-" * 80
    #
    for i in nacl:
        for r in i['ingress']:
            #print "INGRESS", r, "nacl:", i['name']
            print "INGRESS", r
        for r in i['egress']:
            #print "ENGRESS", r, "nacl:", i['name']
            print "ENGRESS", r

    print
    print "-" * 80
    print "Security Groups"
    print "-" * 80

    for i in sg:
        print i['name'], i['description']
        for r in i['ingress']:
            #print "INGRESS", r, "security_group:", i['name']
            print "  INGRESS", r
        for r in i['egress']:
            #print "EGRESS", r, "security_group:", i['name']
            print "  EGRESS ", r
        print

    print
    print
