from JumpScale import j


class Actions():

    def init(self):
        pass

    def getClient(self):
        """
        return client towards g8 master
        """
        return j.clients.openvcloud.get("$(g8.url)", '$(g8.login)', '$(g8.password)')
