
from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self):

        clientaysi = self.service.getProducers("g8client")[0]

        if self.service.hrd.get("g8.account") == "":
            self.service.hrd.set("g8.account", clientaysi.hrd.get("g8.login"))

        if self.service.hrd.get("g8.location") == "":

            cl = self.getClient()
            locations = cl.api.cloudapi.locations.list()

            loc2set = ""

            if len(locations) == 1:
                loc2set = locations[0]["name"]
            else:
                for space in cl.api.cloudapi.cloudspaces.list():
                    if space["name"] == self.service.instance:
                        loc2set = space['location']
            self.service.hrd.set('g8.location', loc2set)

    def install(self):
        client = self.getClient()
        acc = client.account_get(self.service.hrd.get('g8.account'))
        space = acc.space_get(self.service.instance, self.service.hrd.get('g8.location'))

    def uninstall(self):
        client = self.getClient()
        acc = client.account_get(self.service.hrd.get('g8.account'))
        space = acc.space_get(self.service.instance, self.service.hrd.get('g8.location'))
        client.api.cloudapi.cloudspaces.delete(id=space.id)

    def getClient(self):
        g8client = self.service.getProducers("g8client")[0]
        return g8client.actions.getClient()
