from JumpScale import j


class Actions():

    def getExecutor(self):
        addr = self.service.parent.producers['os'][0].hrd.getStr('ssh.addr')
        port = self.service.parent.hrd.get('docker.sshport')
        return j.tools.executor.getSSHBased(addr, port, 'root')

    def install(self):
        if 'sshkey' in self.service.producers:
            sshkey = self.service.producers['sshkey'][0]
            sshkey_priv = sshkey.hrd.get('key.priv')
            sshkey_pub = sshkey.hrd.get('key.pub')
        else:
            raise j.exceptions.NotFound("No sshkey found. please consume an sshkey service")

        print("authorize ssh key to machine")
        cuisine = self.service.actions.getExecutor().cuisine

        cuisine.core.file_write('/root/.ssh/id_rsa', sshkey_priv, mode='0600')
        cuisine.core.file_write('/root/.ssh/id_rsa.pub', sshkey_pub, mode='0600')

        self.service.actions.dns()
        self.service.actions.caddy()
        cuisine.apps.influxdb.start()
        cuisine.apps.mongodb.start()
        cuisine.apps.controller.start()
        self.service.actions.portal()
        self.service.actions.shellinaboxd()
        self.service.actions.grafana()
        self.service.actions.robot()
        self.service.actions.gid()

    def action_dns(self):
        def get_dns_client():
            if 'dns_client' not in self.service.producers:
                raise j.exceptions.AYSNotFound("No dns client found in producers")

            dns_client = self.service.producers['dns_client'][0]
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
        ip = self.service.parent.hrd.getStr('node.addr')
        domain = self.service.hrd.getStr('dns.domain')

        if not domain.endswith('.barcelona.aydo.com'):  # TODO chagne DNS
            domain = '%s.barcelona.aydo.com' % domain
            self.service.hrd.set('dns.domain', domain)
        # Test if domain name is available
        exists, host = dns_client.exists(domain)
        if exists and host != ip:
            raise j.exceptions.Input("Domain %s is not available, please choose another one." % domain)

        dns_client.setRecordA(domain, ip, ttl=120) # TODO, set real TTL

    def action_grafana(self):
        cuisine = self.service.actions.getExecutor().cuisine
        cuisine.apps.grafana.start()
        cfg = cuisine.core.file_read('$cfgDir/grafana/grafana.ini')
        cfg = cfg.replace('domain = localhost', 'domain = $(domain)')
        cfg = cfg.replace('root_url = %(protocol)s://%(domain)s:%(http_port)s/', 'root_url = %(protocol)s://%(domain)s:%(http_port)s/grafana')
        cuisine.core.file_write('$cfgDir/grafana/grafana.ini', cfg)
        # restart to take in account new config
        cuisine.processmanager.stop("grafana-server")
        cuisine.processmanager.start("grafana-server")
        # Add dashboard and datasource
        from JumpScale.clients.cockpit import GrafanaData
        domain = self.service.hrd.getStr('dns.domain')
        cl = j.clients.grafana.get('https://%s/grafana/' % domain, username='admin', password='admin')
        cl.updateDashboard(GrafanaData.dashboard['dashboard'])
        cl.addDataSource(GrafanaData.datasource)
        cl.changePassword(self.service.hrd.getStr('portal.password'))

    def action_portal(self):
        cuisine = self.service.actions.getExecutor().cuisine
        cuisine.apps.portal.start(force=True, passwd="$(portal.password)")
        # link required cockpit spaces
        cuisine.core.dir_ensure('$cfgDir/portals/main/base/')
        cuisine.core.file_link("/opt/code/github/jumpscale/jumpscale_portal8/apps/gridportal/base/Cockpit", "$cfgDir/portals/main/base/Cockpit")
        cuisine.core.file_link("/opt/code/github/jumpscale/jumpscale_portal8/apps/gridportal/base/AYS", "$cfgDir/portals/main/base/AYS")
        cuisine.core.file_link("/opt/code/github/jumpscale/jumpscale_portal8/apps/gridportal/base/system__atyourservice", "$cfgDir/portals/main/base/system__atyourservice")
        # restart portal to load new spaces
        cuisine.processmanager.stop('portal')
        cuisine.processmanager.start('portal')

    def action_shellinaboxd(self):
        cuisine = self.service.actions.getExecutor().cuisine
        # TODO: authorize local sshkey to auto login
        config = "-s '/:root:root:/:ssh root@localhost'"
        cmd = 'shellinaboxd --disable-ssl --port 4200 %s ' % config
        cuisine.processmanager.ensure('shellinabox_cockpit', cmd=cmd)

    def action_caddy(self):
        cuisine = self.service.actions.getExecutor().cuisine
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
        """

        caddy_portal_cfg = "proxy / 127.0.0.1:82"
        shellinbox_url = j.data.idgenerator.generateXCharID(15)
        caddy_main_cfg = caddy_main_cfg.replace("$hostname", self.service.hrd.getStr('dns.domain'))
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

    def action_robot(self):
        cuisine = self.service.actions.getExecutor().cuisine
        cmd = "ays bot --token %s" % self.service.hrd.getStr('telegram.token')
        cuisine.tmux.executeInScreen('aysrobot', 'aysrobot', cmd, wait=0)

    def action_gid(self):
        cuisine = self.service.actions.getExecutor().cuisine
        content = "grid.id = %d\nnode.id = 0" % self.service.hrd.getInt('gid')
        cuisine.core.file_append(location="$hrdDir/system/system.hrd", content=content)