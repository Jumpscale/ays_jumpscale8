

class Actions(ActionsBaseMgmt):

    def init(self):
        if service.hrd.getBool('aysfs', False):
            service.aysrepo.new('aysfs', args={'os': service.instance}, parent=service)

        # if weave:
        #     instantiate weave
        # if agent:
        #     instantiate agent
        # sshkey = service.aysrepo.getService(role='sshkey', instance=service.hrd.getStr('sshkey'))
        # service.hrd.set("ssh.key.public", sshkey.hrd.get("key.pub"))
        # service.hrd.set("ssh.key.private", sshkey.hrd.get("key.priv"))

        # if service.hrd.get("system.backdoor.passwd").strip() == "":
        #     service.hrd.set("system.backdoor.passwd", j.data.idgenerator.generateXCharID(12))
        return True

    def getExecutor(self):
        return j.tools.executor.getSSHBased(service.hrd.get("ssh.addr"), service.hrd.getInt("ssh.port"), 'root')

    def monitor(self):
        j.sal.nettools.tcpPortConnectionTest(service.hrd.get("ssh.addr"), service.hrd.getInt("ssh.port"), timeout=5)
        j.clients.ssh.get(service.hrd.get("ssh.addr"), port=service.hrd.getInt("ssh.port"), login='root', passwd=None, stdout=True, forward_agent=False, allow_agent=True, look_for_keys=True, timeout=5, testConnection=True, die=True)


    def install(self):
        if 'sshkey' in service.producers:
            sshkey = service.producers['sshkey'][0]
            sshkey_pub = sshkey.hrd.get('key.pub')
        else:
            raise RuntimeError("No sshkey found. please consume an sshkey service")

        print("authorize ssh key to machine")

        executor = service.actions.getExecutor()
        cuisine = executor.cuisine

        cuisine.ssh.authorize('root', sshkey_pub)
