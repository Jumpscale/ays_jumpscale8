
from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self, service):
        pass

    def install(self, service):
        client = self.getClient(service)
        # create vdc if it doesn't exists
        if not client.api.system.usermanager.userexists(name='$(username)'):
            groups = service.hrd.getList('groups')
            client.api.system.usermanager.create(username='$(username)', password='$(password)', groups=groups, emails=['$(email)'], domain='')
        # authorize user to all consumed vdc
        for vdc in service.producers['vdc']:
            acc = client.account_get(vdc.hrd.get('g8.account'))
            space = acc.space_get(vdc.instance, vdc.hrd.get('g8.location'))
            username = service.hrd.getStr('username')
            if username not in [u['userGroupId'] for u in space.model['acl']]:
                client.api.cloudapi.cloudspaces.addUser(cloudspaceId=space.id, userId=username, accesstype="ARCXDU")

    def uninstall(self, service):
        # unauthorize user to all consumed vdc
        for vdc in service.producers['vdc']:
            acc = client.account_get(vdc.hrd.get('g8.account'))
            space = acc.space_get(vdc.instance, vdc.hrd.get('g8.location'))
            client.api.cloudapi.cloudspaces.deleteUser(cloudspaceId=space.id, userId='$(username)', recursivedelete=True)

    def getClient(self, service):
        g8client = service.producers['g8client'][0]
        return g8client.actions.getClient(g8client)
