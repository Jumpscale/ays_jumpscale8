from JumpScale import j

ActionsBase = self.service.aysrepo.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    # def _generateProxies(self):
    #     proxies = []
    #     for docker in self.service.hrd.getList('backends'):
    #             # path = "/webaccess/%s/%s" % (docker, j.data.idgenerator.generateXCharID(15))
    #             # backend = "localhost:4200/%s" % docker
    #             proxy = """proxy / localhost:4200""".format(path=path, backend=backend)
    #             proxies.append(proxy)
    #     return proxies

    def _registerDomain(self):
        if 'skydnsclient' not in self.service.producers:
            raise RuntimeError("No skydns client found, please make sure this service consume a skydns client")

        cl = self.service.producers['skydnsclient'][0].action_methods_mgmt.getClient()
        domain = self.service.hrd.getStr('domain')
        target = self.service.parent.parent.hrd.getStr('machine.publicip')
        print(cl.setRecordA(domain, target, ttl=300))

    def showProxyURL(self):
        print("OUT: Accessible dockers : ")
        ip = self.service.parent.parent.hrd.getStr('machine.publicip')
        for docker in self.service.hrd.getList('backends'):
            url = "http://%s/%s" % (ip, docker)
            print("OUT: ", url)

    def install(self):
        self._registerDomain()

        # self.service.hrd.set('proxy.backends', self._getBackends())
        cuisine = self.service.parent.action_methods_mgmt.getExecutor().cuisine
        # domain = self.service.hrd.getStr('domain')
        # backends = self.service.hrd.getStr('proxy.backends')
        shellinabox = self.service.getProducers('shellinabox')
        if not shellinabox:
            address = 'localhost'
        else:
            address = shellinabox[0].parent.parent.hrd.get('machine.publicip')
        tmpl = """
:80
gzip
log /optvar/cfg/caddy/log/access.log
errors {
    log /optvar/cfg/caddy/log/errors.log
}
root /optvar/cfg/caddy/www

proxy / %s:4200
""" % address
        # for proxy in self._generateProxies():
        #     tmpl += '\n%s' % proxy

        cuisine.file_write('$cfgDir/caddy/caddyfile.conf', tmpl)
        cuisine.dir_ensure('/optvar/cfg/caddy/log/')
        cuisine.dir_ensure('/optvar/cfg/caddy/www')
        cfgPath = cuisine.args_replace("$cfgDir/caddy/caddyfile.conf")
        cmd = '$binDir/caddy -conf=%s -email=info@greenitglobe.com' % (cfgPath)
        cuisine.processmanager.ensure('caddy', cmd)

        self.showProxyURL()
