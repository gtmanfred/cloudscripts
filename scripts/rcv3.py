#!/usr/bin/env python
"""
This is for pulling down all of the load balancer pools using the

http://docs.rcv3.apiary.io

It lists the load balancer pools and vips, then it lists the servers in that
load balancer pool with the uuid of the server.

# Example:
    python scripts/rcv3.py --username <username> --apikey <apikey> --region <REGION>

# Requirements:
    requests
"""
from __future__ import print_function
import argparse

from libs.rcv3 import RCv3


def main():
    parser = argparse.ArgumentParser(description='List rcv3 loadbalancer pools and servers in them.')
    parser.add_argument('-u', '--username', required=True, type=str, help='Username for cloud account')
    parser.add_argument('-a', '--apikey', required=True, type=str, help='Apikey for cloud account')
    regions = ('IAD', 'ORD', 'LON', 'HKG', 'SYD')
    parser.add_argument('-r', '--region', required=True, type=str, choices=regions, help='Region for cloud account')
    args = parser.parse_args()

    this = RCv3(args.username, apikey=args.apikey, region=args.region.lower())

    for pool in this.pools:
        print('\n{name}:'.format(**pool))
        print('\tUUID: {id}'.format(**pool))
        print('\tIP: {virtual_ip}'.format(**pool))
        print('\tCloud Servers:')
        for cloudserver in this.cloudservers(pool['id']):
            print('\t\t{name}: {id}'.format(**cloudserver['cloud_server']))


if __name__ == '__main__':
    main()
