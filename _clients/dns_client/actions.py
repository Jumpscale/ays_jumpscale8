from JumpScale import j


class Actions(ActionsBaseMgmt):

    #@todo wrong, this is not an action method, should not use these as clients or implement library functions
    def get_client(self, service):
        addr = service.hrd.getStr('addr')
        port = service.hrd.getInt('port', 22)
        login = service.hrd.getStr('login', "root")
        password = service.hrd.getStr('password', None)
        if password == '':
            password = None
        sshkey_producers = service.producers.get('sshkey', None)
        pubkey = ''
        if sshkey_producers:
            sshkey_service = sshkey_producers[0]
            # make sure key is loaded in ssh-agent
            sshkey_service.actions.start(service=sshkey_service)
            pubkey = sshkey_service.hrd.getStr('key.path').strip(' "')
        cuisine = j.tools.executor.getSSHBased(addr=addr, port=port, passwd=password, login=login).cuisine
        cuisine._executor.authorizeKey(pubkey=pubkey)
        return cuisine.apps.geodns
