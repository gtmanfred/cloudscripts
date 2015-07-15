from libs.auth import Auth

ENDPOINT='https://{0}.rackconnect.api.rackspacecloud.com/v3/{1}'

class RCv3(Auth):
    @property
    def rc3endpoint(self):
        return ENDPOINT.format(self.region.lower(), self.tenant)

    @property
    def pools(self):
        return self.sess.get('{0}/load_balancer_pools'.format(
            self.rc3endpoint
        )).json()

    def cloudservers(self, poolid):
        endpoint=ENDPOINT.format(self.region.lower(), self.tenant)
        return self.sess.get((
            '{0}/load_balancer_pools/{1}/nodes/details'
        ).format(self.rc3endpoint, poolid)).json()
