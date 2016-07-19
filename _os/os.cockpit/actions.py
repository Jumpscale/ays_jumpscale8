from JumpScale import j


class Actions(ActionsBaseMgmt):

    def getExecutor(self, service):
        addr = service.parent.producers['os'][0].hrd.getStr('ssh.addr')
        port = service.parent.hrd.get('docker.sshport')
        sshkey = service.producers.get('sshkey')[0]
        return j.tools.executor.getSSHBased(addr, port, 'root', pushkey=sshkey.hrd.get('ssh.keypath'))

    def install(self, service):
        if 'sshkey' in service.producers:
            sshkey = service.producers['sshkey'][0]
            sshkey_priv = sshkey.hrd.getStr('key.priv')
            sshkey_pub = sshkey.hrd.getStr('key.pub')
        else:
            raise j.exceptions.NotFound("No sshkey found. please consume an sshkey service")

        print("authorize ssh key to machine")
        cuisine = self.getExecutor(service).cuisine

        cuisine.core.file_write('/root/.ssh/id_rsa', sshkey_priv, mode='0600')
        cuisine.core.file_write('/root/.ssh/id_rsa.pub', sshkey_pub, mode='0600')
        if cuisine.core.file_exists('/root/.ssh/authorized_keys'):
            cuisine.core.file_append('/root/.ssh/authorized_keys', sshkey_pub)
        else:
            cuisine.core.file_write('/root/.ssh/authorized_keys', sshkey_pub)

        self.dns(service=service)
        self.caddy(service=service)
        cuisine.apps.influxdb.start()
        cuisine.apps.mongodb.start()
        cuisine.apps.controller.start()
        self.portal(service=service)
        self.shellinaboxd(service=service)
        self.grafana(service=service)
        self.gid(service=service)
        self.cockpit(service=service)
        self.ays_repo(service=service)

        cuisine.user.passwd("root", j.data.idgenerator.generateGUID())

    @action()
    def dns(self, service):
        def get_dns_clients():
            if 'dns_client' not in service.producers:
                raise j.exceptions.AYSNotFound("No dns client found in producers")

            clients = []
            for s in service.producers['dns_client']:
                clients.append(s.actions.get_client(s))
            return clients

        ip = service.parent.hrd.getStr('node.addr')
        domain = service.hrd.getStr('dns.domain')
        domain_root = '.' + service.hrd.getStr('dns.root')
        split_count = domain_root.count('.') - 1

        if not domain.endswith(domain_root):
            domain = domain + domain_root
            service.hrd.set('dns.domain', domain)
        subdomain = '.'.join(domain.split('.', split_count)[:split_count])

        # set domain to all dns servers
        dns_clients = get_dns_clients()
        for dns_client in dns_clients:
            if domain not in dns_client.domains:
                domain = dns_client.ensure_domain('.'.join(domain_root.split('.')[-2:]))
            if subdomain in domain._a_records:
                records = domain._a_records[subdomain]
                ips = [r[0] for r in records if r]
                if ip not in ips:
                    raise j.exceptions.Input("Domain %s is not available, please choose another one." % domain)
            else:
                domain.add_a_record(ip, subdomain)
                domain.save()

    @action()
    def grafana(self, service):
        cuisine = self.getExecutor(service).cuisine
        cuisine.apps.grafana.start()
        cfg = cuisine.core.file_read('$cfgDir/grafana/grafana.ini')
        cfg = cfg.replace('domain = localhost', 'domain = %s' % service.hrd.getStr('dns.domain'))
        cfg = cfg.replace('root_url = %(protocol)s://%(domain)s:%(http_port)s/', 'root_url = %(protocol)s://%(domain)s:%(http_port)s/grafana')
        cuisine.core.file_write('$cfgDir/grafana/grafana.ini', cfg)
        # restart to take in account new config
        cuisine.processmanager.stop("grafana-server")
        cuisine.processmanager.start("grafana-server")
        # Add dashboard and datasource
        repo_url = cuisine.core.args_replace('$codeDir/github/jumpscale/jscockpit')
        if not j.sal.fs.exists(repo_url):
            j.tools.cuisine.local.git.pullRepo(url='https://github.com/Jumpscale/jscockpit.git')
        dashboard = j.data.serializer.json.load(repo_url + '/deployer_bot/templates/dashboard.json')
        datasource = j.data.serializer.json.load(repo_url + '/deployer_bot/templates/datasource.json')
        domain = service.hrd.getStr('dns.domain')
        cl = j.clients.grafana.get('https://%s/grafana/' % domain, username='admin', password='admin', verify_ssl=False)
        cl.updateDashboard(dashboard['dashboard'])
        cl.addDataSource(datasource)

    @action()
    def portal(self, service):
        cuisine = self.getExecutor(service).cuisine
        cuisine.apps.portal.start(force=True)
        # link required cockpit spaces
        cuisine.core.dir_ensure('$cfgDir/portals/main/base/')
        cuisine.core.file_link("$codeDir/github/jumpscale/jscockpit/apps/Cockpit", "$cfgDir/portals/main/base/Cockpit")
        content = cuisine.core.file_read("$cfgDir/portals/main/config.hrd")
        hrd = j.data.hrd.get(content=content, prefixWithName=False)
        hrd.set('param.cfg.force_oauth_instance', 'itsyou.online')
        hrd.set('param.cfg.client_url', 'https://itsyou.online/v1/oauth/authorize')
        hrd.set('param.cfg.token_url', 'https://itsyou.online/v1/oauth/access_token')
        hrd.set('param.cfg.redirect_url', 'https://%s/restmachine/system/oauth/authorize' % service.hrd.getStr('dns.domain'))
        hrd.set('param.cfg.client_scope', 'user:email:main,user:memberof:%s' % service.hrd.getStr('oauth.organization'))
        hrd.set('param.cfg.organization', service.hrd.getStr('oauth.organization'))
        hrd.set('param.cfg.client_id', service.hrd.getStr('oauth.client_id'))
        hrd.set('param.cfg.client_secret', service.hrd.getStr('oauth.client_secret'))
        hrd.set('param.cfg.client_user_info_url', 'https://itsyou.online/api/users')
        hrd.set('param.cfg.oauth.default_groups', ['admin', 'user'])
        hrd.set('param.cfg.client_logout_url', '')
        hrd.set('param.cfg.defaultspace', 'home'),
        hrd.set('param.cfg.cockpit', {'host': 'localhost', 'port': 5000}),
        content = cuisine.core.file_write("$cfgDir/portals/main/config.hrd", str(hrd))
        self.generate_home(service)
        # restart portal to load new spaces
        cuisine.processmanager.stop('portal')
        cuisine.processmanager.start('portal')

    @action()
    def shellinaboxd(self, service):
        cuisine = self.getExecutor(service).cuisine
        # TODO: authorize local sshkey to auto login
        config = "-s '/:root:root:/:ssh root@localhost'"
        cmd = 'shellinaboxd --disable-ssl --port 4200 %s ' % config
        cuisine.processmanager.ensure('shellinabox_cockpit', cmd=cmd)

    @action()
    def caddy(self, service):
        cuisine = self.getExecutor(service).cuisine
        caddy_main_cfg = """
        $hostname
        gzip

        log /optvar/cfg/caddy/log/portal.access.log
        errors {
        log /optvar//cfg/caddy/log/portal.errors.log
        }

        import $varDir/cfg/caddy/proxies/*
        """
        caddy_proxy_cfg = """
        redir /apidocs/api.raml /api/apidocs/api.raml 301

        proxy /$shellinbox_url 127.0.0.1:4200 {
            without /$shellinbox_url
        }

        proxy /0/0/hubble 127.0.0.1:8966 {
          without /0/0/hubble
          websocket
        }

        proxy /controller 127.0.0.1:8966 {
           without /controller
           websocket
        }

        proxy /grafana 127.0.0.1:3000 {
            without /grafana
        }

        proxy /api 127.0.0.1:5000 {
            without /api
        }
        """

        domain = service.hrd.getStr('dns.domain')
        caddy_portal_cfg = "proxy / 127.0.0.1:82"
        shellinbox_url = j.data.idgenerator.generateXCharID(15)
        service.hrd.set('shellinabox.url', shellinbox_url)
        caddy_main_cfg = caddy_main_cfg.replace("$hostname", domain)
        caddy_main_cfg = cuisine.core.args_replace(caddy_main_cfg)
        caddy_proxy_cfg = caddy_proxy_cfg.replace("$shellinbox_url", shellinbox_url)
        cuisine.core.dir_ensure('$varDir/cfg/caddy/log')
        cuisine.core.dir_ensure('$varDir/cfg/caddy/proxies/')
        cuisine.core.file_write('$varDir/cfg/caddy/caddyfile', caddy_main_cfg)
        cuisine.core.file_write('$varDir/cfg/caddy/proxies/01_proxies', caddy_proxy_cfg)
        cuisine.core.file_write('$varDir/cfg/caddy/proxies/99_portal', caddy_portal_cfg)

        cmd = '$binDir/caddy -conf $varDir/cfg/caddy/caddyfile -email mail@fake.com -http2=false'
        if service.hrd.getBool('staging', False):
            # enable stating environment, remove for prodction
            cmd += ' -ca https://acme-staging.api.letsencrypt.org/directory'
        cuisine.processmanager.ensure('caddy', cmd)

    @action()
    def gid(self, service):
        cuisine = self.getExecutor(service).cuisine
        content = "grid.id = %d\nnode.id = 0" % service.hrd.getInt('gid')
        if not cuisine.core.file_exists("$hrdDir/system/system.hrd"):
            cuisine.core.file_write(location="$hrdDir/system/system.hrd", content=content)
        else:
            cuisine.core.file_append(location="$hrdDir/system/system.hrd", content=content)

    @action()
    def cockpit(self, service):
        cuisine = self.getExecutor(service).cuisine
        token = service.hrd.getStr('telegram.token')
        jwt_key = service.hrd.getStr('oauth.jwt_key')
        organization = service.hrd.getStr('oauth.organization')
        client_id = service.hrd.getStr('oauth.client_id')
        client_secret = service.hrd.getStr('oauth.client_secret')
        domain = service.hrd.getStr('dns.domain')
        redirect_uri = 'https://%s/api/oauth/callback' % domain
        cuisine.apps.cockpit.start(
            bot_token=token,
            jwt_key=jwt_key,
            organization=organization,
            client_secret=client_secret,
            client_id=client_id,
            redirect_uri=redirect_uri,
            itsyouonlinehost='https://itsyou.online')

    @action()
    def ays_repo(self, service):
        url = service.hrd.getStr('ays.repo.url', None)
        if not url:
            return
        cuisine = self.getExecutor(service).cuisine
        cuisine.core.dir_ensure('/opt/code/cockpit')
        cuisine.core.run('cd /opt/code/cockpit;git init; git remote add origin %s' % url)
        cuisine.executor.upload(service.aysrepo.basepath, '/opt/code/cockpit/ays_cockpit')

    def generate_home(self, service):
        tmpl = """# Welcome to the Cockpit of {organization}

To have access to all the functionalities of the cockpit please sign in by using the login button in the top right corner.


Usefull links to start using the cockpit:
* [cockpit information](/cockpit/information)
* [API documentation](/api/apidocs/index.html?raml=api.raml)
"""
        organization = service.hrd.getStr('oauth.organization')
        content = tmpl.format(organization=organization)
        cuisine = self.getExecutor(service).cuisine
        cuisine.core.file_write("$cfgDir/portals/main/base/home/home.md", content)
