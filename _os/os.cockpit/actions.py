from JumpScale import j


class Actions(ActionsBaseMgmt):

    def getExecutor(self, service):
        addr = service.parent.producers['os'][0].hrd.getStr('ssh.addr')
        port = service.parent.hrd.get('docker.sshport')
        return j.tools.executor.getSSHBased(addr, port, 'root')

    def install(self, service):
        if 'sshkey' in service.producers:
            sshkey = service.producers['sshkey'][0]
            sshkey_priv = sshkey.hrd.get('key.priv')
            sshkey_pub = sshkey.hrd.get('key.pub')
        else:
            raise j.exceptions.NotFound("No sshkey found. please consume an sshkey service")

        print("authorize ssh key to machine")
        cuisine = self.getExecutor(service).cuisine

        cuisine.core.file_write('/root/.ssh/id_rsa', sshkey_priv, mode='0600')
        cuisine.core.file_write('/root/.ssh/id_rsa.pub', sshkey_pub, mode='0600')

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

    @action()
    def dns(self, service):
        def get_dns_client():
            if 'dns_client' not in service.producers:
                raise j.exceptions.AYSNotFound("No dns client found in producers")

            dns_client = service.producers['dns_client'][0]
            client = None
            url = dns_client.hrd.get('url')
            login = dns_client.hrd.get('login')
            passwd = dns_client.hrd.get('password')

            try:
                client = j.clients.skydns.get(url, username=login, password=passwd)
                cfg = client.getConfig()
                if 'error' in cfg:
                    client = None
            except Exception as e:
                client = None
            if not client:
                raise j.exceptions.RuntimeError("Can't connect to DNS cluster at %s" % url)
            return client

        dns_client = get_dns_client()
        ip = service.parent.hrd.getStr('node.addr')
        domain = service.hrd.getStr('dns.domain')

        if not domain.endswith('.barcelona.aydo.com'):  # TODO chagne DNS
            domain = '%s.barcelona.aydo.com' % domain
            service.hrd.set('dns.domain', domain)
        # Test if domain name is available
        exists, host = dns_client.exists(domain)
        if exists and host != ip:
            raise j.exceptions.Input("Domain %s is not available, please choose another one." % domain)

        dns_client.setRecordA(domain, ip, ttl=120) # TODO, set real TTL

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
        from JumpScale.clients.cockpit import GrafanaData
        domain = service.hrd.getStr('dns.domain')
        cl = j.clients.grafana.get('https://%s/grafana/' % domain, username='admin', password='admin')
        cl.updateDashboard(GrafanaData.dashboard['dashboard'])
        cl.addDataSource(GrafanaData.datasource)

    @action()
    def portal(self, service):
        cuisine = self.getExecutor(service).cuisine
        cuisine.apps.portal.start(force=True)
        # link required cockpit spaces
        cuisine.core.dir_ensure('$cfgDir/portals/main/base/')
        cuisine.core.file_link("/opt/code/github/jumpscale/jumpscale_portal8/apps/gridportal/base/Cockpit", "$cfgDir/portals/main/base/Cockpit")
        cuisine.core.file_link("/opt/code/github/jumpscale/jumpscale_portal8/apps/gridportal/base/AYS", "$cfgDir/portals/main/base/AYS")
        cuisine.core.file_link("/opt/code/github/jumpscale/jumpscale_portal8/apps/gridportal/base/system__atyourservice", "$cfgDir/portals/main/base/system__atyourservice")
        content = cuisine.core.file_read("$cfgDir/portals/main/config.hrd")
        hrd = j.data.hrd.get(content=content, prefixWithName=False)
        hrd.set('param.cfg.force_oauth_instance', 'itsyou.online')
        hrd.set('param.cfg.client_url', 'https://itsyou.online/v1/oauth/authorize')
        hrd.set('param.cfg.token_url', 'https://itsyou.online/v1/oauth/access_token')
        hrd.set('param.cfg.redirect_url', 'https://%s/restmachine/system/oauth/authorize' % service.hrd.getStr('dns.domain'))
        hrd.set('param.cfg.client_scope', 'user:admin,user:memberof:%s' % service.hrd.getStr('oauth.organization'))
        hrd.set('param.cfg.client_id', service.hrd.getStr('oauth.client_id'))
        hrd.set('param.cfg.client_secret', service.hrd.getStr('oauth.client_secret'))
        hrd.set('param.cfg.client_user_info_url', 'https://itsyou.online/users/')
        hrd.set('param.cfg.client_logout_url', '')
        content = cuisine.core.file_write("$cfgDir/portals/main/config.hrd", str(hrd))

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
        proxy /0/0/hubble 127.0.0.1:8966 {
          without /0/0/hubble
          websocket
        }

        proxy /controller 127.0.0.1:8966 {
           without /controller
           websocket
        }

        proxy /$shellinbox_url 127.0.0.1:4200 {
           without /$shellinbox_url
        }

        proxy /grafana 127.0.0.1:3000 {
            without /grafana
        }

        proxy /api 127.0.0.1:5000 {
            without /api
        }
        """

        caddy_portal_cfg = "proxy / 127.0.0.1:82"
        shellinbox_url = j.data.idgenerator.generateXCharID(15)
        caddy_main_cfg = caddy_main_cfg.replace("$hostname", service.hrd.getStr('dns.domain'))
        caddy_main_cfg = cuisine.core.args_replace(caddy_main_cfg)
        caddy_proxy_cfg = caddy_proxy_cfg.replace("$shellinbox_url", shellinbox_url)
        cuisine.core.dir_ensure('$varDir/cfg/caddy/log')
        cuisine.core.dir_ensure('$varDir/cfg/caddy/proxies/')
        cuisine.core.file_write('$varDir/cfg/caddy/caddyfile', caddy_main_cfg)
        cuisine.core.file_write('$varDir/cfg/caddy/proxies/01_proxies', caddy_proxy_cfg)
        cuisine.core.file_write('$varDir/cfg/caddy/proxies/99_portal', caddy_portal_cfg)

        cmd = '$binDir/caddy -conf $varDir/cfg/caddy/caddyfile -email mail@fake.com -http2=false'
        # enable stating environment, remove for prodction
        # cmd += ' -ca https://acme-staging.api.letsencrypt.org/directory'
        cuisine.processmanager.ensure('caddy', cmd)

    @action()
    def gid(self, service):
        cuisine = self.getExecutor(service).cuisine
        content = "grid.id = %d\nnode.id = 0" % service.hrd.getInt('gid')
        cuisine.core.file_append(location="$hrdDir/system/system.hrd", content=content)

    @action()
    def cockpit(self, service):
        cuisine = self.getExecutor(service).cuisine
        token = service.hrd.getStr('telegram.token')
        jwt_key = service.hrd.getStr('oauth.jwt_key')
        organization = service.hrd.getStr('oauth.organization')
        cuisine.apps.cockpit.start(token, jwt_key, organization)
