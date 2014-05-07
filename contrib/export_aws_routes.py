#!/usr/bin/env python
from recordkeeper.api import find_records
import sys
from netaddr import IPNetwork, IPAddress

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
    rtb = instance2rtb(instance)

    print "instance:", instance['name'], "id:", instance['instances']
    print "=" * 80
    show_routes(rtb)

