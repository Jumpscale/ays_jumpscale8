
from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self, service):
        pass

    def install(self, service):
        client = self.getClient(service)
        # create vdc if it doesn't exists
        username = service.hrd.getStr('username')
        password = service.hrd.getStr('password')
        email = service.hrd.getStr('email')
        provider = service.hrd.getStr('provider', None)
        username = "%s@%s" % (username, provider) if provider else username
        if not client.api.system.usermanager.userexists(name=username):
            groups = service.hrd.getList('groups')
            client.api.system.usermanager.create(username=username, password=password, groups=groups, emails=[email], domain='', provider=provider)
        # authorize user to all consumed vdc
        for vdc in service.producers.get('vdc', []):
            acc = client.account_get(vdc.hrd.get('g8.account'))
            space = acc.space_get(vdc.instance, vdc.hrd.get('g8.location'))
            if username not in [u['userGroupId'] for u in space.model['acl']]:
                client.api.cloudapi.cloudspaces.addUser(cloudspaceId=space.id, userId=username, accesstype="ARCXDU")

    def uninstall(self, service):
        # unauthorize user to all consumed vdc
        client = self.getClient(service)
        username = service.hrd.getStr('username')
        provider = service.hrd.getStr('provider', None)
        username = "%s@%s" % (username, provider) if provider else username
        for vdc in service.producers('vdc', []):
            acc = client.account_get(vdc.hrd.get('g8.account'))
            space = acc.space_get(vdc.instance, vdc.hrd.get('g8.location'))
            client.api.cloudapi.cloudspaces.deleteUser(cloudspaceId=space.id, userId=username, recursivedelete=True)

    def getClient(self, service):
        g8clients = service.producers.get('g8client', None)
        if g8clients is not None:
            return g8client[0].actions.getClient(g8client)
        else:
            raise j.exceptions.NotFound("Not produer g8cient found.")
