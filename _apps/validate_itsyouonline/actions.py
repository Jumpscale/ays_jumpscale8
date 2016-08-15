from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self, service):
        import urllib
        import requests
        import json

        # get jwt token
        client_id = service.hrd.getStr("oauth.client_id")
        client_secret = service.hrd.getStr("oauth.client_secret")
        params = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        url = 'https://itsyou.online/v1/oauth/access_token?%s' % (urllib.parse.urlencode(params))
        resp = requests.post(url, verify=False)
        resp.raise_for_status()
        access_token = resp.json()['access_token']

        url = 'https://itsyou.online/v1/oauth/jwt'
        headers = {'Authorization': 'token %s' % access_token}
        data = {
            'scope': 'user:memberOf:%s' % (client_id)
        }
        resp = requests.post(url, data=json.dumps(data), headers=headers, verify=False)

        jwt = resp.text
        print("JWT:", jwt)

        # domain = service.hrd.getStr('dns.domain')
        # client = j.clients.cockpit.getClient(domain, jwt)
        # blueprints = client.listBlueprints('js8tests')
        # for blueprint in blueprints:
        #     client.executeBlueprint('js8tests', blueprint['name'])
