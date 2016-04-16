

class Actions:

    def init(self):
        if self.service.hrd.getBool('aysfs', False):
            j.atyourservice.new('aysfs', args={'os': self.service.instance}, parent=self.service)

        # if weave:
        #     instantiate weave
        # if agent:
        #     instantiate agent
        # sshkey = j.atyourservice.getService(role='sshkey', instance=self.service.hrd.getStr('sshkey'))
        # self.service.hrd.set("ssh.key.public", sshkey.hrd.get("key.pub"))
        # self.service.hrd.set("ssh.key.private", sshkey.hrd.get("key.priv"))

        # if self.service.hrd.get("system.backdoor.passwd").strip() == "":
        #     self.service.hrd.set("system.backdoor.passwd", j.data.idgenerator.generateXCharID(12))
        return True

    def getExecutor(self):
        return j.tools.executor.getSSHBased(self.service.hrd.get("ssh.addr"), self.service.hrd.getInt("ssh.port"), 'root')

    def monitor(self):
        j.sal.nettools.tcpPortConnectionTest(self.service.hrd.get("ssh.addr"), self.service.hrd.getInt("ssh.port"), timeout=5)
        j.clients.ssh.get(self.service.hrd.get("ssh.addr"), port=self.service.hrd.getInt("ssh.port"), login='root', passwd=None, stdout=True, forward_agent=False, allow_agent=True, look_for_keys=True, timeout=5, testConnection=True, die=True)


    def install(self):
        if 'sshkey' in self.service.producers:
            sshkey = self.service.producers['sshkey'][0]
            sshkey_pub = sshkey.hrd.get('key.pub')
        else:
            raise RuntimeError("No sshkey found. please consume an sshkey service")

        print("authorize ssh key to machine")

        executor = self.service.actions.getExecutor()
        cuisine = executor.cuisine

        cuisine.ssh.authorize('root', sshkey_pub)
