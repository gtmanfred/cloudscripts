# -*- coding: utf-8 -*-
from __future__ import absolute_import
from .auth import Auth

ENDPOINT='https://{0}.rackconnect.api.rackspacecloud.com/v3/{1}'


class RCv3(Auth):
    """
    Class for getting information about rackconnect v3 setup

    http://docs.rcv3.apiary.io/
    """
    @property
    def rc3endpoint(self):
        """Api endpoint for rcv3 apis"""
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
