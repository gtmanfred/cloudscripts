import argparse

from auth import Auth


def main():
    parser = argparse.ArgumentParser(description='List rcv3 loadbalancer pools and servers in them.')
    parser.add_argument('-u', '--username', required=True, type=str, help='Username for cloud account')
    parser.add_argument('-a', '--apikey', required=True, type=str, help='Apikey for cloud account')
    regions = ('IAD', 'ORD', 'LON', 'HKG', 'SYD')
    parser.add_argument('-r', '--region', required=True, type=str, choices=regions, help='Region for cloud account')
    args = parser.parse_args()

    this = Auth(args.username, args.apikey, args.region.lower(), 'cloudServersOpenStack')

    rc3endpoint='https://{0}.rackconnect.api.rackspacecloud.com/v3/{1}'.format(this.region.lower(), this.tenant)

    pools = this.sess.get('{0}/load_balancer_pools'.format(rc3endpoint)).json()

    for pool in pools:
        print('{name}: {virtual_ip}'.format(**pool))
        cloudservers = this.sess.get('{0}/load_balancer_pools/{1}/nodes/details'.format(rc3endpoint, pool['id'])).json()
        for cloudserver in cloudservers:
            print('\t{name}: {id}'.format(**cloudserver['cloud_server']))


if __name__ == '__main__':
    main()
