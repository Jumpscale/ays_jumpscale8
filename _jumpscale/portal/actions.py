from JumpScale import j


class Actions(ActionsBaseMgmt):

    def add_user(self, service):
        cmd = 'jsuser list'
        res = service.executor.cuisine.core.run(cmd, profile=True)
        for line in res.splitlines():
            if line.find('$(admin.login)') != -1:
                return True

        cmd = 'jsuser add -d $(admin.login):$(admin.passwd):admin:admin@fake_email.com:fake_domain.com'
        service.executor.cuisine.core.run(cmd, profile=True)

    def install(self, service):

        service.executor.cuisine.apps.portal.install(start=True)

        for space in service.hrd.getList('spaces'):
            space = j.sal.fs.joinPaths(service.executor.cuisine.core.dir_paths['codeDir'], space)
            service.executor.cuisine.apps.portal.addSpace(space)
        for actor in service.hrd.getList('spaces'):
            actor = j.sal.fs.joinPaths(service.executor.cuisine.core.dir_paths['codeDir'], actor)
            service.executor.cuisine.apps.portal.addActor(actor)
        self.add_user(service)
