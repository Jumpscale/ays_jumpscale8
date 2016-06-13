from JumpScale import j


class Actions(ActionsBaseMgmt):

    def get_client(self, service):
        """
        return client towards packet.net
        """
        import packet
        token = service.hrd.getStr('packet.token')
        client = packet.Manager(token)
        return client
