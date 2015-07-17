# -*- coding: utf-8 -*-
from __future__ import absolute_import
try:
    from urllib.parse import quote as urlquote
except ImportError as exc:
    from urllib import quote as urlquote

from .auth import Auth


class Servers(Auth):
    """
    Class for getting information about cloud servers

    http://docs.rackspace.com/servers/api/v2/cs-devguide/content/ch_preface.html
    """
    def __init__(self, username, region, apikey=None, password=None):
        super(Servers, self).__init__(username, region.upper(), apikey,
                                     password, endname='cloudServersOpenStack')

    @property
    def servers(self):
        return self.sess.get(
            '{publicURL}/servers/detail'.format(**self.endpoint)
        ).json()

    @property
    def flavors(self):
        return self.sess.get(
            '{publicURL}/flavors/detail'.format(**self.endpoint)
        ).json()

    def get_servers(self, name):
        return self.sess.get(
            '{publicURL}/servers/detail?name={name}'.format(
                name=urlquote(name), **self.endpoint
            )
        ).json()

