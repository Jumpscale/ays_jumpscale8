from JumpScale import j


class Actions(ActionsBaseMgmt):

    def add_user(self, service):
        cmd = 'jsuser list'
        res = self.cuisine.run(cmd, profile=True)
        for line in res.splitlines():
            if line.find('$(admin.login)') != -1:
                return True

        cmd = 'jsuser add -d $(admin.login):$(admin.passwd):admin:admin@fake_email.com:fake_domain.com'
        self.cuisine.run(cmd, profile=True)

    def install(self, service):
        mongo_ip, mongo_port = '$mongocfg'.split(':') if '$(mongocfg)' and ':' in '$(mongocfg)' else '127.0.0.1', '27017'
        influx_ip, influx_port = '$influxcfg'.split(':') if '$(influxcfg)' and ':' in '$(influxcfg)' else '127.0.0.1', '8086'
        grafana_ip, grafana_port = '$grafanacfg'.split(':') if '$(grafanacfg)' and ':' in '$(grafanacfg)' else '127.0.0.1', '3000'

        service.executor.cuisine.apps.portal.install(start=True, mongodbip=mongo_ip, mongoport=mongo_port, influxip=influx_ip,
                                                    influxport=influx_port, grafanaip=grafana_ip, grafanaport=grafana_port)

        for space in service.hrd.getList('spaces'):
            space = j.sal.fs.joinPaths(service.executor.cuisine.core.dir_paths['codeDir'], space)
            service.executor.cuisine.apps.portal.addSpace(space)
        for actor in service.hrd.getList('spaces'):
            actor = j.sal.fs.joinPaths(service.executor.cuisine.core.dir_paths['codeDir'], actor)
            service.executor.cuisine.apps.portal.addActor(actor)
        self.add_user()
