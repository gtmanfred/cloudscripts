# -*- coding: utf-8 -*-
from __future__ import absolute_import
import copy
import json
import os.path
import base64
import time

try:
    from urllib.parse import quote as urlquote
except ImportError as exc:
    from urllib import quote as urlquote

from .auth import Auth
from .images import Images
from .utils import valid_uuid


class Server(object):
    def __init__(self, server, servers):
        self.servers = servers
        for key, value in server.items():
            setattr(self, key, value)

    def _update(self, server=None):
        if server is None:
            server = self.servers.get_server_by_uuid(self.id)
        dict_ = self.__dict__
        dict_.update(server.__dict__)
        for key, value in dict_.items():
            setattr(self, key, value)

    def wait(self, stat='ACTIVE'):
        while not hasattr(self, 'status'):
            time.sleep(1)
            self._update()
        while self.status != stat:
            if self.status == 'ERROR':
                raise Exception(
                    'Server in error status: {0}'.format(s['name'])
                )
            time.sleep(1)
            self._update()
        return

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
        resp = self.sess.get(
            '{publicURL}/servers/detail'.format(**self.endpoint)
        ).json().get('servers', [])
        ret = []
        for s in resp:
            ret.append(Server(s, self))
        return ret

    def get_server_by_uuid(self, uuid):
        for server in self.servers:
            if server.id == uuid:
                return server
        return None

    def get_servers_by_name(self, name):
        resp = self.sess.get(
            '{publicURL}/servers/detail?name={name}'.format(
                name=urlquote(name), **self.endpoint
            )
        ).json().get('servers', [])
        ret = []
        for s in resp:
            ret.append(Server(s, self))
        return ret

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
        return None

    @property
    def keypairs(self):
        return self.sess.get(
            '{publicURL}/os-keypairs'.format(**self.endpoint)
        ).json().get('keypairs', [])

    def keypair_exists(self, name):
        for keypair in self.keypairs:
            if keypair['name'].startswith(name):
                return True
        return False

    @property
    def networks(self):
        return self.sess.get(
            '{publicURL}/os-networksv2'.format(**self.endpoint)
        ).json().get('networks', [])

    def get_network_by_name(self, name):
        for network in self.networks:
            if network['label'] == name:
                return network
        return {}

    def get_network_by_uuid(self, uuid):
        for network in self.networks:
            if network['id'] == uuid:
                return network
        return {}

    def _validate_inputs(self, vm_):
        args = ['flavorRef', 'name', 'imageRef', 'OS-DCF:diskConfig',
                'metadata', 'networks', 'key_name', 'config_drive',
                'personality', 'user_data']

        ret = {'name': vm_['name']}

        flavor = self.get_flavor_by_name(vm_['flavorRef'])
        if flavor is not None:
            ret['flavorRef'] = flavor
        else:
            raise Exception('Flavor not found: {flavorRef}'.format(**vm_))

        image = self.images.get_image_by_name(vm_['imageRef'])
        if image is not None:
            ret['imageRef'] = image
        else:
            raise Exception('Image not found: {imageRef}'.format(**vm_))

        if vm_.get('OS-DCF:diskConfig', None) in ('AUTO', 'MANUAL'):
            ret['OS-DCF:diskConfig'] = vm_['OS-DCF:diskConfig']
        else:
            ret['OS-DCF:diskConfig'] = 'MANUAL'

        if 'key_name' in vm_ and self.keypair_exists(vm_['key_name']):
            ret['key_name'] = vm_['key_name']

        if vm_.get('config_drive', None) in (True, False):
            ret['config_drive'] = vm_['config_drive']
        else:
            ret['config_drive'] = False

        ret['networks'] = []
        for network in vm_['networks']:
            if self.get_network_by_uuid(network):
                ret['networks'].append({'uuid': network})
            else:
                net = self.get_network_by_name(network)
                if net:
                    ret['networks'].append({'uuid': net['id']})

        ret['metadata'] = {}
        KeyTypes = (str)
        ValueTypes = (int, str, bool)
        for key, value in vm_.get('metadata', {}).items():
            if isinstance(key, KeyTypes) and isinstance(value, ValueTypes):
                ret['metadata'][key] = value

        ret['personality'] = []
        for p in vm_.get('personality', []):
            if not hasattr(p, 'path') or not hasattr(p, 'contents'):
                continue
            tmp = {'path': p['path']}
            if hasattr(p['contents'], 'read'):
                tmp['contents'] = base64.b64encode(p['contents'].read())
            elif os.path.exists(p['contents']):
                with open(p['contents']) as contentsfile:
                    tmp['contents'] = base64.b64encode(contentsfile.read())
            else:
                tmp['contents'] = base64.b64encode(p['contents'])
            ret['personality'].append(tmp)

        if 'user_data' in vm_:
            if hasattr(vm_['user_data'], 'read'):
                ret['user_data'] = base64.b64encode(vm_['user_data'].read())
            elif os.path.exists(u):
                with open(vm_['user_data']) as userdatafile:
                    ret['user_data'] = base64.b64encode(userdatafile.read())
            else:
                ret['user_data'] = base64.b64encode(vm_['user_data'])
        
        return ret

    def create_server(self, name, image, flavor, networks=None, **kwargs):
        vm_ = copy.deepcopy(kwargs)
        vm_['name'] = name
        vm_['imageRef'] = image
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

        vm_['networks'] = networks

        vm_ = self._validate_inputs(vm_)

        resp = self.sess.post(
            '{publicURL}/servers'.format(**self.endpoint),
            data=json.dumps({'server': vm_}),
        ).json().get('server', {})
        if resp:
            return Server(resp, self)
        return False

    def delete_server(self, name=None, uuid=None):
        if name is None and uuid is None:
            raise Exception('Requires one: name or uuid')
        if uuid is None:
            server = self.get_servers_by_name(name)
            if len(server) > 1:
                raise Exception('More than one server with name: {0}'.format(name))
            elif len(server) == 0:
                raise Exception('No server with name: {0}'.format(name))
            else:
                server = server[0]
        else:
            server = object()
            server.id = uuid

        resp = self.sess.delete('{0}/servers/{1}'.format(
            self.endpoint['publicURL'],
            server.id
        ))

        if 300 > resp.status_code >= 200:
            return True
        return False

    def wait(self, uuid):
        s = self.get_server_by_uuid(uuid)
        while getattr(s, 'status', None) != 'ACTIVE':
            if getattr(s, 'status', None) == 'ERROR':
                raise Exception(
                    'Server in error status: {0}'.format(s['name'])
                )
            time.sleep(1)
            s = self.get_server_by_uuid(uuid)
        return
