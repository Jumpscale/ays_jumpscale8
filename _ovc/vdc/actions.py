
from JumpScale import j


class Actions():

    def init(self):
        pass

    def getClient(self):
        clientname = """$(producer.g8client)"""
        clientname = clientname.strip().strip("',")
        g8client = j.atyourservice.getServiceFromKey(clientname)
        return g8client.actions.getClient()
