# -*- coding: utf-8 -*-
import requests
import json
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

IDENTITY='https://identity.api.rackspacecloud.com/v2.0/tokens'

class Auth(object):
    """
    Base class for all cloud scripts.

    http://docs.rackspace.com/
    """
    def __init__(self, username, region, apikey=None,
                 password=None, endname=None, cloudfeed=None):
        if all([x is None for x in [password, apikey]]):
            raise Exception('Password or Apikey must be provided')
        self.username = username
        self.sess = requests.Session()
        if apikey is not None:
            resp = self._apikey(apikey)
        elif password is not None:
            resp = self._password(password)
        self.token = resp['access']['token']['id']
        self.tenant = resp['access']['token']['tenant']['id']
        self.sess.headers['X-Auth-Token'] = self.token
        self.catalog = resp['access']['serviceCatalog']
        self.region = region
        self.endname = endname
        self.cloudfeed = cloudfeed

    def _password(self, password):
        data = {
            "auth":{
                "passwordCredentials":{
                    "username": self.username,
                    "password": password
                }
            }
        }
        self.sess.headers = {
            'Content-type': 'application/json',
        }
        return self.sess.post(IDENTITY, data=json.dumps(data)).json()

    def _apikey(self, apikey):
        data = {
            "auth":{
                "RAX-KSKEY:apiKeyCredentials":{
                    "username": self.username,
                    "apiKey": apikey
                }
            }
        }
        self.sess.headers = {
            'Content-type': 'application/json',
        }
        return self.sess.post(IDENTITY, data=json.dumps(data)).json()

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
            ret = self.sess.get(ret['publicURL'], headers={'Accept': 'application/vnd.rackspace.atom+json'}).json()
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
