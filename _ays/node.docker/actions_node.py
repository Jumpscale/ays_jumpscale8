from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassNode()


class Actions(ActionsBase):

    def connnectDockerHost(self, serviceObj):
        baseurl = serviceObj.hrd.getStr('docker.baseurl')
        if baseurl != "localhost":
            if baseurl.find(':') != -1:
                addr, port = baseurl.split(":")
            else:
                addr = baseurl
                port = 2375
            j.sal.docker.connectRemoteTCP(addr, port)

    def install(self, serviceObj):
        """
        will install create a docker container
        """

        pubkey=serviceObj.hrd.getStr("ssh.key.public")
        ports = serviceObj.hrd.getStr('docker.portsforwards', None)
        volumes = serviceObj.hrd.getStr('docker.volumes', None)
        # installJS = serviceObj.hrd.getBool('jumpscale', False)

        self.connnectDockerHost(serviceObj)
        container =j.sal.docker.create(name=serviceObj.instance, stdout=True, base="$(docker.image)",
                              ports=ports, vols=volumes,sshpubkey=pubkey,
                              jumpscale=False, sharecode=serviceObj.hrd.getBool('jumpscale.sharecode'))

        serviceObj.hrd.set("ssh.port", container.ssh_port)
        _, ip = j.sal.nettools.getDefaultIPConfig()
        serviceObj.hrd.set("node.tcp.addr", j.sal.docker.remote['host'])

    def removedata(self, serviceObj):
        """
        delete docker container
        """
        self.connnectDockerHost(serviceObj)
        j.sal.docker.destroy(serviceObj.instance)
        return True

    def start(self, serviceObj):
        self.connnectDockerHost(serviceObj)
        c = j.sal.docker.get(serviceObj.instance)
        c.restart()

    def stop(self, serviceObj):
        self.connnectDockerHost(serviceObj)
        c = j.sal.docker.get(serviceObj.instance)
        c.stop()
