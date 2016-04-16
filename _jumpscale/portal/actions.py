from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def __init__(self, service):
        super(Actions, self).__init__(service)
        self.service = service
        self._cuisine = None
        self.dockermap = None

    @property
    def cuisine(self):
        if not self._cuisine:
            self._cuisine = self.service.parent.action_methods_mgmt.getExecutor().cuisine
        return self._cuisine

    def addUser(self):
        cmd = 'jsuser list'
        res = self.cuisine.run(cmd, profile=True)
        for line in res.splitlines():
            if line.find('demo') != -1:
                return True

        cmd = 'jsuser add -d demo:$(demo.user.passwd):$(demo.user.groups):$(demo.user.email):$(demo.user.domain)'
        self.cuisine.run(cmd, profile=True)

    def install(self):
        monogcluster = self.service.getProducers('mongocluster')[0]
        clusterconfig = monogcluster.hrd.getDict('clusterconfig')

        for host, config in clusterconfig.items():
            if 'mongos:' in config:
                port = config.split('mongos:')[1]
                port = port.split()[0].strip()
                break

        content = self.cuisine.file_read('$cfgDir/portals/example/config.hrd')
        hrd = j.data.hrd.get(content=content, prefixWithName=False)
        cfg = {'host': host, 'port': int(port)}
        hrd.set('param.mongoengine.connection', cfg)
        self.cuisine.file_write('$cfgDir/portals/example/config.hrd', str(hrd))
        self.addcmd()

    def addcmd(self):
        pm = self.cuisine.processmanager.get(pm='tmux')
        pm.ensure(name='portal_%s' % self.service.instance, cmd='jspython portal_start.py', path='$cfgDir/portals/example')

    def load(self):
        self.addcmd()
        self.cuisine.processmanager.start('portal_%s' % self.service.instance)

    def halt(self):
        self.addcmd()
        self.cuisine.processmanager.stop('portal_%s' % self.service.instance)
        