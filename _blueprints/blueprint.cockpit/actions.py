from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self):
        g8_url = self.service.hrd.getStr('g8.url')
        g8_login = self.service.hrd.getStr('g8.login')
        g8_password = self.service.hrd.getStr('g8.password')
        g8_account = self.service.hrd.getStr('g8.account')
        dns_login = self.service.hrd.getStr('dns.login')
        dns_password = self.service.hrd.getStr('dns.password')
        cockpit_name = self.service.hrd.getStr('cockpit.name')
        telegram_token = self.service.hrd.getStr('telegram.token')
        portal_password = self.service.hrd.getStr('portal.password')

        args = {'g8.url': g8_url,
                'g8.login': g8_login,
                'g8.password': g8_password}
        g8_client = self.service.aysrepo.new('g8client', args=args, instance="main")

        args = {
            'url': 'https://dns1.aydo.com/etcd',
            'login': dns_login,
            'password': dns_password
        }
        dns_client = self.service.aysrepo.new('dns_client', args=args, instance="main")

        sshkey = self.service.aysrepo.new('sshkey', instance="main")

        vdcfarm = self.service.aysrepo.new('vdcfarm', instance="main")

        args = {
            'g8.account': g8_account,
            'g8.client.name': g8_client.instance
        }
        vdc = self.service.aysrepo.new('vdc', args=args, instance=cockpit_name, parent=vdcfarm)

        args = {'ports': '80:80, 443:443, 18384:18384'}
        node_ovc = self.service.aysrepo.new('node.ovc', args=args, instance="cockpitvm", parent=vdc)

        args = {
            'node': node_ovc.instance
        }
        os = self.service.aysrepo.new('os.ssh.ubuntu', args=args, instance=self.service.instance, parent=node_ovc)

        args = {
            "image": "jumpscale/g8cockpit",
            'os': os.instance,
            'aysfs': False,
            'ports': '80, 443, 18384'
        }
        docker = self.service.aysrepo.new('node.docker', args=args, instance="cockpit", parent=os)

        args = {
            'aysfs': True,
            "telegram.token": telegram_token,
            "gid": 1,
            "portal.password": portal_password,
            "dns.domain": g8_login,
            'node': docker.instance,
            'dns_client': dns_client.instance
        }
        cockpit = self.service.aysrepo.new('os.cockpit', args=args, instance=cockpit_name, parent=docker)
