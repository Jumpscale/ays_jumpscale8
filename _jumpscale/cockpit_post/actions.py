from JumpScale import j


class Actions(ActionsBaseMgmt):

    def install(self, service):
        cuisine = service.executor.cuisine
        for url in service.hrd.getList('repos'):
            cuisine.git.pullRepo(url)

        # add sshkey to cockpit!
        sshkey = service.producers.get('sshkey')
        pubkey = sshkey.hrd.get('key.pub')
        cuisine.ssh.authorize('root', pubkey)
