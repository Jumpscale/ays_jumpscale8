
from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self, service):

        clientaysi = service.getProducers("g8client")[0]

        if service.hrd.get("g8.account") == "":
            service.hrd.set("g8.account", clientaysi.hrd.get("g8.account"), clientaysi.hrd.get("g8.login"))

        if service.hrd.get("g8.location") == "":

            cl = self.getClient(service)
            locations = cl.api.cloudapi.locations.list()

            loc2set = ""

            if len(locations) == 1:
                loc2set = locations[0]["name"]
            else:
                for space in cl.api.cloudapi.cloudspaces.list():
                    if space["name"] == service.instance:
                        loc2set = space['location']
            service.hrd.set('g8.location', loc2set)

    def install(self, service):
        client = self.getClient(service)
        acc = client.account_get(service.hrd.get('g8.account'))

        if service.hrd.exists('vdc.id'):  # this is an update
            space = acc.space_get(name=service.instance, location=service.hrd.get('g8.location'), create=False)
            space.model['maxMemoryCapacity'] = service.hrd.getInt('maxmemorycapacity'),
            space.model['maxVDiskCapacity'] = service.hrd.getInt('maxvdiskcapacity'),
            space.model['maxCPUCapacity'] = service.hrd.getInt('maxcpucapacity'),
            space.model['maxNASCapacity'] = service.hrd.getInt('maxnascapacity'),
            space.model['maxArchiveCapacity'] = service.hrd.getInt('maxarchivecapacity'),
            space.model['maxNetworkOptTransfer'] = service.hrd.getInt('maxnetworkopttransfer'),
            space.model['maxNetworkPeerTransfer'] = service.hrd.getInt('maxnetworkpeertransfer'),
            space.model['maxNumPublicIP'] = service.hrd.getInt('maxnumpublicip')
            space.save()
        else:  # creation
            space = acc.space_get(name=service.instance,
                                  location=service.hrd.get('g8.location'),
                                  create=True,
                                  maxMemoryCapacity=service.hrd.getInt('maxmemorycapacity'),
                                  maxVDiskCapacity=service.hrd.getInt('maxvdiskcapacity'),
                                  maxCPUCapacity=service.hrd.getInt('maxcpucapacity'),
                                  maxNASCapacity=service.hrd.getInt('maxnascapacity'),
                                  maxArchiveCapacity=service.hrd.getInt('maxarchivecapacity'),
                                  maxNetworkOptTransfer=service.hrd.getInt('maxnetworkopttransfer'),
                                  maxNetworkPeerTransfer=service.hrd.getInt('maxnetworkpeertransfer'),
                                  maxNumPublicIP=service.hrd.getInt('maxnumpublicip')
                                  )
            service.hrd.set('vdc.id', space.id)

        to_be_authorize = set()
        if 'ovc_user' in service.producers:
            # some user have access to this space, make sure only the user consumed have access.
            for user in service.producers['ovc_user']:
                username = user.hrd.getStr('username')
                provider = user.hrd.getStr('provider', None)
                username = "%s@%s" % (username, provider) if provider else username
                to_be_authorize.add(username)

        to_be_unauthorize = set(space.authorized_users).difference(to_be_authorize)
        # remove the user account that created the space from the to_be_unauthorize set.
        for account in acc.model['acl']:
            to_be_unauthorize.remove(account['userGroupId'])

        for username in to_be_authorize:
            space.authorize_user(username)
        for username in to_be_unauthorize:
            space.unauthorize_user(username)

    def uninstall(self, service):
        client = self.getClient(service)
        acc = client.account_get(service.hrd.get('g8.account'))
        space = acc.space_get(service.instance, service.hrd.get('g8.location'))
        client.api.cloudapi.cloudspaces.delete(cloudspaceId=space.id)
        if service.hrd.exists('vdc.id'):
            service.hrd.delete('vdc.id')

    def getClient(self, service):
        g8client = service.getProducers("g8client")[0]
        return g8client.actions.getClient(g8client)
