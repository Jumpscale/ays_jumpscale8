from JumpScale import j

ActionsBase = service.aysrepo.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def __init__(self, service):
        super(Actions, self).__init__(service)
        self._dockerhost = None
        self._dockerssh = None
        self._portmap = dict()

    @property
    def dockerhost(self, service):
        return service.parent

    def getExecutor(self, service):
        sshkey = service.getProducers('sshkey')[0]
        keypath = j.sal.fs.joinPaths(sshkey.path, 'key_%s.pub' % sshkey.hrd.get('key.name'))
        addr = getattr(self.dockerhost.action_methods_mgmt.cuisine.executor, 'addr', 'localhost')
        executor = j.tools.executor.getSSHBased(addr=addr, port=service.hrd.getInt('sshport'))
        executor.authorizeKey(keyname=keypath)
        return executor


    @property
    def portmap(self, service):
        if self._portmap:
            return self._portmap
        if service.hrd.get('dockermap', {}):
            dockermap = service.hrd.getDict('dockermap')
            return {int(local): int(public) for local, public in dockermap.items()}

    def _findFreePort(self, takenports):
        dockerport = 8122
        while True:
            if dockerport in takenports:
                dockerport += 1
            else:
                return dockerport

    def _createPortForwards(self, portfwardmap):
        host = self.dockerhost.action_methods_mgmt.getMachine()
        for vmport, spaceport in portfwardmap.items():
            print(vmport, '--->', spaceport)
            host.create_portforwarding(spaceport, vmport)

    def _createMap(self, source):
        portforwards = service.hrd.getList('ports')
        portmap = dict()
        for port in portforwards:
            if port.find(':') != -1:
                port, toport = port.split(":")
                port, toport = int(port), int(toport)
            else:
                toport = self._findFreePort(source)
                port = int(port)
            source.append(toport)
            portmap[port] = toport
        return portmap

    def install(self, service):
        cuisine = self.dockerhost.action_methods_mgmt.cuisine
        # cuisine.bash.include('/opt/jumpscale8/env.sh')

        space = self.dockerhost.action_methods_mgmt.getSpace()
        spaceports = [int(portforward['publicPort']) for portforward in space.portforwardings]

        self._portmap = self._createMap(spaceports)

        # service.hrd.set('dockermap', '\n'.join(['%i:%i,' % (local, public) for local, public in self._portmap.items()]))
        service.hrd.set('dockermap', self._portmap)

        openports = self.dockerhost.action_methods_mgmt.cuisine.run("ss -al", showout=False)
        vmports = list()
        for line in openports.splitlines():
            item = line.split()[4].strip()
            item = item.rsplit(':', 1)[1] if ':' in item else None
            port = int(item) if item and j.data.types.int.checkString(item) else None
            if port:
                vmports.append(port)

        dockermap = self._createMap(vmports)

        portforwards = ' '.join(['%i:%i' % (local, public) for local, public in dockermap.items()])

        sshkey = service.getProducers('sshkey')[0]
        pubkey = sshkey.hrd.get('key.pub')
        portforwards = "-p '%s'" % portforwards if portforwards else ""
        image = service.hrd.getStr('image')
        cuisine.run("/opt/jumpscale8/bin/jsdocker create -i %s -n %s %s --pubkey '%s' --aysfs" % (image, service.instance, portforwards, pubkey), profile=True)
        sshport = cuisine.run('docker port %s 22' % service.instance)
        if ':' in sshport:
            sshport = sshport.rsplit(':', 1)[1]

        spaceport = self._findFreePort(spaceports)
        while spaceport in list(dockermap.keys()):
            spaceport = self._findFreePort(spaceport)

        pfmap = {int(sshport): spaceport}

        service.hrd.set('sshport', spaceport)
        for dockerport, vmport in dockermap.items():
            pfmap[vmport] = self._portmap[dockerport]

        self._createPortForwards(pfmap)

        if service.hrd.getBool('shellinabox'):
            recipe = service.aysrepo.getRecipe('shellinabox')
            recipe.newInstance(instance=service.instance, consume=service)


        # prepare docker with js paths
        # executor = self.getExecutor()
        # executor.cuisine.bash.addPath('/opt/jumpscale8/bin/')
        # executor.cuisine.bash.environSet('PYTHONPATH', '/opt/jumpscale8/lib/:$PYTHONPATH')

        # make sure docker is registered in caddy and shellinabox if set to do so
        # local = j.tools.cuisine.get()
        # fw = "%s/%s" % (service.instance, j.data.idgenerator.generateXCharID(15))
        # if service.hrd.getBool('caddyproxy'):
        #     rc, _ = local.run('which caddy', die=False)
        #     if rc:
        #         local.builder.caddy()
        #     path = "/webaccess/%s" % (fw)
        #     backend = "localhost:4200/%s" % service.instance
        #     proxy = """proxy {path} {backend}""".format(path=path, backend=backend)
        #
        #     local.file_append('$cfgDir/caddy/caddyfile.conf', '\n%s' % proxy)
        #     cfgPath = local.args_replace("$cfgDir/caddy/caddyfile.conf")
        #     cmd = '$binDir/caddy -conf=%s -email=info@greenitglobe.com' % (cfgPath)
        #     local.processmanager.ensure('caddy', cmd)
        #     local.processmanager.stop('caddy')
        #     local.processmanager.start('caddy')
        #
        # if service.hrd.getBool('shellinabox'):
        #     rc, _ = local.run('which shellinaboxd', die=False)
        #     if rc:
        #         local.package.install('shellinabox')
        #     dockerip = service.parent.hrd.get('machine.publicip').strip()
        #     path = ('$cfgDir/shellinabox')
        #     config = local.file_read(path).splitlines()
        #     config.append('/%s:root:root:/:ssh root@%s -p %s' % (fw, dockerip, self.hrd.get('sshport')))
        #     siabparams = ' '.join(config)
        #     local.file_write(path, '\n'.join(config))
        #     local.run('service shellinabox stop', die=False)
        #
        #     cmd = 'shellinaboxd --disable-ssl %s ' % siabparams
        #     local.processmanager.ensure('shellinabox', cmd=cmd)
        #     local.processmanager.restart('shellinabox')
