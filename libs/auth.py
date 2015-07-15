import requests
import json
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

IDENTITY='https://identity.api.rackspacecloud.com/v2.0/tokens'

class Auth(object):
    def __init__(self, username, apikey, region, endname, cloudfeed=None):
        self.sess = requests.Session()
        data = {
            "auth":{
                "RAX-KSKEY:apiKeyCredentials":{
                    "username": username,
                    "apiKey": apikey
                }
            }
        }
        self.sess.headers = {
            'Content-type': 'application/json',
        }
        resp = self.sess.post(IDENTITY, data=json.dumps(data)).json()
        self.token = resp['access']['token']['id']
        self.tenant = resp['access']['token']['tenant']['id']
        self.sess.headers['X-Auth-Token'] = self.token
        self.catalog = resp['access']['serviceCatalog']
        self.region = region
        self.endname = endname
        self.cloudfeed = cloudfeed

    @property
    def _endpoints(self):
        for service in self.catalog:
            if service['name'] == self.endname:
                return service['endpoints']

    @property
    def endpoint(self):
        for endpoint in self._endpoints:
            if endpoint['region'] == self.region:
                ret = endpoint
                break
        if self.endname == 'cloudFeeds':
            ret = self.sess.get(ret['publicURL'], headers={'Accept': 'application/vnd.rackspace.atom+json'}).json()
        return ret

    @property
    def cloudfeedurl(self):
        for feed in self.endpoint['service']['workspace']:
            if feed['title'] == self.cloudfeed:
                return feed

    @property
    def tenantid(self):
        return self.endpoint['tenantId']
