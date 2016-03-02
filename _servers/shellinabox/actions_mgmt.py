from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):
    def install(self):
        executor = self.service.parent.action_methods_mgmt.getExecutor()
        executor.cuisine.package.install('shellinabox')
        dockernames = self.service.hrd.getList('backends')
        config = list()

        for dockername in dockernames:
            docker = j.atyourservice.getService(role='docker', instance=dockername.strip())
            dockerip = docker.parent.hrd.get('machine.publicip').strip()
            if executor.addr == dockerip:
                dockerip = '127.0.0.1'
            config.append("-s '/%s:root:root:/:ssh root@%s -p %s'" % (dockername, dockerip, docker.hrd.get('sshport')))

        siabparams = ' '.join(config)
        self.service.hrd.set('config', siabparams)
        executor.cuisine.run('service shellinabox stop')

        cmd = 'shellinaboxd --disable-ssl %s ' % siabparams
        executor.cuisine.processmanager.ensure('shellinabox', cmd=cmd)
