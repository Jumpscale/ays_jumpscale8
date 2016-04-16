
from JumpScale import j


class Actions():

    def init(self):
        pass

    def getClient(self):
        clientname="$(g8.client.name)"
        g8client=j.atyourservice.getService("g8client",instance=clientname)
        return g8client.actions.getClient()
        
