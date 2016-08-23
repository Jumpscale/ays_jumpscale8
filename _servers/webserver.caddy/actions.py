from JumpScale import j

class Actions(ActionsBaseMgmt):

    def add_proxy(self, service, path, address, port=80, trimPrefix=True):
        proxy = "proxy {path} {address}:{port}".format(path=path, address=address, port=port)
        if trimPrefix:
            proxy += '{\n without %s\n}' % path

        cfg = service.executor.cuisine.core.file_read("$cfgDir/caddy/caddyfile.conf")
        cfg += '\n%s' % proxy

        service.executor.cuisine.core.file_write("$cfgDir/caddy/caddyfile.conf", cfg)
        service.executor.cuisine.processmanager.stop('caddy')
        service.executor.cuisine.processmanager.start('caddy')

    def _registerDomain(self, service):
        if 'dns_client' not in service.producers:
            raise j.exceptions.NotFound("No skydns client found, please make sure this service consume a skydns client")

        dns_client = service.producers['dns_client'][0]
        cl = j.clients.skydns.get(
            baseurl=dns_client.hrd.getStr('url'),
            username=dns_client.hrd.getStr('login'),
            password=dns_client.hrd.getStr('password'))

        domain = service.hrd.getStr('domain')
        target = service.parent.hrd.getStr('ssh.addr')
        cl.setRecordA(domain, target)
        return domain

    def install(self, service):
        cuisine = service.executor.cuisine

        domain = self._registerDomain(service)
        path = cuisine.bash.cmdGetPath('caddy', die=False)
        if not path:
            cuisine.apps.caddy.install(start=True, ssl=True, dns=domain)
        else:
            cuisine.apps.caddy.start(ssl=True)
