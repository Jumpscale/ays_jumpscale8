
from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self):

        clientaysi = service.getProducers("g8client")[0]

        if service.hrd.get("g8.account") == "":
            service.hrd.set("g8.account", clientaysi.hrd.get("g8.login"))

        if service.hrd.get("g8.location") == "":

            cl = service.actions.getClient()
            locations = cl.api.cloudapi.locations.list()

            loc2set = ""

            if len(locations) == 1:
                loc2set = locations[0]["name"]
            else:
                for space in cl.api.cloudapi.cloudspaces.list():
                    if space["name"] == service.instance:
                        loc2set = space['location']
            service.hrd.set('g8.location', loc2set)

    def install(self):
        client = service.actions.getClient()
        acc = client.account_get(service.hrd.get('g8.account'))
        space = acc.space_get(service.instance, service.hrd.get('g8.location'))

    def uninstall(self):
        client = service.actions.getClient()
        acc = client.account_get(service.hrd.get('g8.account'))
        space = acc.space_get(service.instance, service.hrd.get('g8.location'))
        client.api.cloudapi.cloudspaces.delete(id=space.id)

    def getClient(self):
        g8client = service.getProducers("g8client")[0]
        return g8client.actions.getClient()
