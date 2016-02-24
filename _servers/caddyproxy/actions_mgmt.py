from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def _getBackends(self):
        backends = []
        if 'portal' in self.service.producers:
            for prod in self.service.producers['portal']:
                addr = "%s:%s" % (prod.instance, int('$(port)'))
                backends.append(addr)
            #     portMap = prod.parent.hrd.getDict('dockermap')
            #     for k, v in portMap.items():
            #         if str(k) == '82':
            #             addr = "%s:%s" % (prod.instance, v)
            #             backends.append(addr)
            #             break
        return ' '.join(backends)

    def _registerDomain(self):
        if 'skydnsclient' not in self.service.producers:
            raise RuntimeError("No skydns client found, please make sure this service consume a skydns client")

        cl = self.service.producers['skydnsclient'][0].action_methods_mgmt.getClient()
        domain = self.service.hrd.getStr('domain')
        target = self.service.parent.parent.hrd.getStr('machine.publicip')
        print(cl.setRecordA(domain, target, ttl=300))

    def install(self):
        self._registerDomain()

        self.service.hrd.set('proxy.backends', self._getBackends())
        cuisine = self.service.parent.action_methods_mgmt.getExecutor().cuisine
        domain = self.service.hrd.getStr('domain')
        backends = self.service.hrd.getStr('proxy.backends')
        tmpl = """
%s
gzip
log /optvar/cfg/caddy/log/access.log
errors {
    log /optvar/cfg/caddy/log/errors.log
}
root /optvar/cfg/caddy/www

proxy / %s {
    proxy_header Host {host}
    proxy_header X-Real-IP {remote}
    proxy_header X-Forwarded-Proto {scheme}
}""" % (domain,backends)
        cuisine.file_write('$cfgDir/caddy/caddyfile.conf', tmpl)
        cuisine.dir_ensure('/optvar/cfg/caddy/log/')
        cuisine.dir_ensure('/optvar/cfg/caddy/www')
        cfgPath = cuisine.args_replace("$cfgDir/caddy/caddyfile.conf")
        cmd = '$binDir/caddy -conf=%s -email=info@greenitglobe.com' % (cfgPath)
        cuisine.processmanager.ensure('caddy', cmd)
