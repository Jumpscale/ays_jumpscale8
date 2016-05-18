from JumpScale import j

ActionsBase = service.aysrepo.getActionsBaseClassMgmt()


class Actions(ActionsBase):
    def install(self, service):
        executor = j.tools.executor.getLocal()
        executor.cuisine.package.install('shellinabox')

        if 'docker' not in service.producers:
            raise RuntimeError("Can't find docker in producers. please comsume a docker service")
        docker = service.producers['docker'][0]

        dockerip = docker.parent.hrd.get('machine.publicip').strip()

        port = 4200
        while j.sal.nettools.tcpPortConnectionTest("localhost", port):
            port += 1
        if j.sal.nettools.tcpPortConnectionTest("localhost", port):
            raise RuntimeError("Can't find free port for shellinabox")

        config = "--port %s -s '/:root:root:/:ssh root@%s -p %s'" % (port, dockerip, docker.hrd.get('sshport'))
        service.hrd.set('config', config)
        service.hrd.set('listen.port', port)
        cmd = 'shellinaboxd --disable-ssl %s ' % config
        executor.cuisine.processmanager.ensure('shellinabox_%s' % service.instance, cmd=cmd)

        if j.sal.process.checkProcessRunning('caddy'):
            # try to configure caddy to proxy shellinabox
            fw = "/%s/%s" % (service.instance, j.data.idgenerator.generateXCharID(15))
            proxy = """
proxy %s 127.0.0.1:%s {
   without %s
}
""" % (fw, port, fw)
            # TODO better config rewriting.
            cfg = executor.cuisine.file_append('$varDir/cfg/caddy/caddyfile', proxy)
            executor.cuisine.processmanager.reload('caddy')

    def start(self, service):
        executor.cuisine.processmanager.start('shellinabox_%s' % service.instance)

    def stop(self, service):
        executor.cuisine.processmanager.stop('shellinabox_%s' % service.instance)

    def uninstall(self, service):
        pass
        # TODO remove config in caddy

