# -*- coding: utf-8 -*-
from __future__ import absolute_import
import copy
import json

try:
    from urllib.parse import quote as urlquote
except ImportError as exc:
    from urllib import quote as urlquote

from .auth import Auth
from .images import Images


class Servers(Auth):
    """
    Class for getting information about cloud servers

    http://docs.rackspace.com/servers/api/v2/cs-devguide/content/ch_preface.html
    """
    def __init__(self, username, region, apikey=None, password=None):
        super(Servers, self).__init__(username, region.upper(), apikey,
                                     password, endname='cloudServersOpenStack')
        self.images = Images(username, region, apikey, password)

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

    def get_flavor_by_name(self, name):
        resp = self.sess.get(
            '{publicURL}/flavors/detail?name={name}'.format(
                name=urlquote(name),
                **self.endpoint
            )
        ).json()
        for flavor in resp.get('flavors', []):
            if flavor['id'] == name or flavor['name'] == name:
                return flavor['id']

    def get_servers(self, name):
        return self.sess.get(
            '{publicURL}/servers/detail?name={name}'.format(
                name=urlquote(name), **self.endpoint
            )
        ).json()

    def create_server(self, name, image, flavor, networks=None, **kwargs):
        vm_ = copy.deepcopy(kwargs)
        vm_['name'] = name
        vm_['imageRef'] = self.images.get_image_by_name(image)
        vm_['flavorRef'] = self.get_flavor_by_name(flavor)
        vm_['OS-DCF:diskConfig'] = 'MANUAL'

        if networks is None:
            networks = {
                '00000000-0000-0000-0000-000000000000',
            }
        if self.is_managed:
            networks.add('11111111-1111-1111-1111-111111111111')
        if self.is_rackconnected == 3:
            networks.discard('00000000-0000-0000-0000-000000000000')

        vm_['networks'] = [{'uuid': x} for x in networks]

        return self.sess.post(
            '{publicURL}/servers'.format(**self.endpoint),
            data=json.dumps({'server': vm_}),
        ).json()
