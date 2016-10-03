

class Actions(ActionsBaseMgmt):

    def init(self, service):
        if service.hrd.getBool('aysfs', False):
            service.aysrepo.new('aysfs', args={'os': service.instance}, parent=service)

        if service.hrd.getBool('weave'):
            weave = service.aysrepo.new('weave', instance=service.instance, parent=service.parent)
        # if agent:
        #     instantiate agent
        # sshkey = service.aysrepo.getService(role='sshkey', instance=service.hrd.getStr('sshkey'))
        # service.hrd.set("ssh.key.public", sshkey.hrd.get("key.pub"))
        # service.hrd.set("ssh.key.private", sshkey.hrd.get("key.priv"))

        # if service.hrd.get("system.backdoor.passwd").strip() == "":
        #     service.hrd.set("system.backdoor.passwd", j.data.idgenerator.generateXCharID(12))
        return True

    def getExecutor(self, service):
        sshkey = service.producers['sshkey'][0]
        pubkey = sshkey.hrd.get('key.pub')
        executor = j.tools.executor.getSSHBased(service.hrd.get("ssh.addr"), service.hrd.getInt("ssh.port"), 'root')
        executor.authorizeKey(pubkey=pubkey)
        return executor

    def monitor(self, service):
        sshkey = service.producers.get('sshkey')[0]
        ssh_path = sshkey.service.hrd.get('key.path')
        sshkey_passphrase = sshkey.service.hrd.get('key.passphrase')

        addr = None
        if service.parent.templatename == 'node.ovc':
            # OVC natting doesn't allow a node to connect to itself
            if service.hrd.exists('private.addr'):
                addr = service.hrd.get('private.addr')
            else:
                return True
        addr = addr or service.hrd.get("ssh.addr")
        j.sal.nettools.tcpPortConnectionTest(addr, service.hrd.getInt("ssh.port"), timeout=5)
        client = j.clients.ssh.get(service.hrd.get("ssh.addr"), port=service.hrd.getInt("ssh.port"), login='root', passwd=None, stdout=True,
                                   forward_agent=False, allow_agent=False, look_for_keys=False, key_filename=ssh_path, passphrase=sshkey_passphrase,
                                   timeout=5, die=True)
        try:
            client.execute('hostname')  # just to make sure connection is valid
            return True
        except Exception as e:
            return False

    def install(self, service):
        if 'sshkey' in service.producers:
            sshkey = service.producers['sshkey'][0]
            sshkey_pub = sshkey.hrd.get('key.pub')
        else:
            raise RuntimeError("No sshkey found. please consume an sshkey service")

        print("authorize ssh key to machine")

        executor = self.getExecutor(service)
        cuisine = executor.cuisine

        for ssh in  service.hrd.getList('authorized_sshkeys', []):
            cuisine.ssh.authorize('root', ssh)

        cuisine.ssh.authorize('root', sshkey_pub)
