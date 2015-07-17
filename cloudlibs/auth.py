# -*- coding: utf-8 -*-
import requests
import json
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

IDENTITY = 'https://identity.api.rackspacecloud.com/v2.0/tokens'


class Auth(object):
    """
    Base class for all cloud scripts.

    http://docs.rackspace.com/
    """
    username = None
    sess = None
    token = None
    tenant = None
    catalog = None
    def __new__(cls, username, region, apikey=None,
                password=None, endname=None, cloudfeed=None):
        if Auth.username is None:
            if all([x is None for x in [password, apikey]]):
                raise Exception('Password or Apikey must be provided')
            Auth.username = username
            Auth.sess = requests.Session()
            if apikey is not None:
                resp = Auth._apikey(apikey)
            elif password is not None:
                resp = Auth._password(password)
            Auth.token = resp['access']['token']['id']
            Auth.tenant = resp['access']['token']['tenant']['id']
            Auth.roles = resp['access']['user']['roles']
            Auth.sess.headers['X-Auth-Token'] = Auth.token
            Auth.catalog = resp['access']['serviceCatalog']
        object.__new__(cls)
        if cls.username is None:
            cls.username = Auth.username
            cls.sess = requests.Session()
            cls.token = Auth.token
            cls.tenant = Auth.tenant
            cls.roles = Auth.roles
            cls.sess.headers['X-Auth-Token'] = cls.token
            cls.catalog = Auth.catalog
        return super(Auth, cls).__new__(cls)

    def __init__(self, username, region, apikey=None,
                 password=None, endname=None, cloudfeed=None):
        self.region = region
        self.endname = endname
        self.cloudfeed = cloudfeed

    @classmethod
    def _password(cls, password):
        data = {
            "auth": {
                "passwordCredentials": {
                    "username": cls.username,
                    "password": password
                }
            }
        }
        cls.sess.headers = {
            'Content-type': 'application/json',
        }
        return cls.sess.post(IDENTITY, data=json.dumps(data)).json()

    @classmethod
    def _apikey(cls, apikey):
        data = {
            "auth": {
                "RAX-KSKEY:apiKeyCredentials": {
                    "username": cls.username,
                    "apiKey": apikey
                }
            }
        }
        cls.sess.headers = {
            'Content-type': 'application/json',
        }
        return cls.sess.post(IDENTITY, data=json.dumps(data)).json()

    @property
    def _endpoints(self):
        for service in self.catalog:
            if service['name'] == self.endname:
                return service['endpoints']

    @property
    def endpoint(self):
        if self.endname is None:
            return None
        for endpoint in self._endpoints:
            if endpoint['region'] == self.region:
                ret = endpoint
                break
        if self.endname == 'cloudFeeds':
            ret = self.sess.get(
                ret['publicURL'],
                headers={'Accept': 'application/vnd.rackspace.atom+json'}
            ).json()
        return ret

    @property
    def cloudfeedurl(self):
        if self.endname is None:
            return None
        for feed in self.endpoint['service']['workspace']:
            if feed['title'] == self.cloudfeed:
                return feed

    @property
    def tenantid(self):
        return self.endpoint['tenantId']

    @property
    def is_rackconnected(self):
        for role in self.roles:
            if role['name'] == 'rack_connect':
                return 2
            if role['name'] == 'rackconnect:v3-{0}'.format(self.region):
                return 3
        return 0

    @property
    def is_managed(self):
        return any([x for x in self.roles if x['name'] == 'rax_managed'])
