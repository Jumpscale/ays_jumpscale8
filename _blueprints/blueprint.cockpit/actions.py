from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self, service):
        cockpit_name = service.hrd.getStr('cockpit.name')

        args = {'g8.url': service.hrd.getStr('g8.url'),
                'g8.login': service.hrd.getStr('g8.login'),
                'g8.password': service.hrd.getStr('g8.password')}
        g8_client = service.aysrepo.new('g8client', args=args, instance="main")

        args = {
            'url': 'https://dns1.aydo.com/etcd',
            'login': service.hrd.getStr('dns.login'),
            'password': service.hrd.getStr('dns.password')
        }
        dns_client = service.aysrepo.new('dns_client', args=args, instance="main")

        sshkey = service.aysrepo.new('sshkey', instance="main")

        vdcfarm = service.aysrepo.new('vdcfarm', instance="main")

        args = {
            'g8.account': service.hrd.getStr('g8.account'),
            'g8.url': service.hrd.getStr('g8.url'),
            'g8.client.name': g8_client.instance
        }
        vdc = service.aysrepo.new('vdc', args=args, instance=cockpit_name, parent=vdcfarm)

        args = {'ports': '80:80, 443:443, 18384:18384'}
        node_ovc = service.aysrepo.new('node.ovc', args=args, instance="cockpitvm", parent=vdc)

        args = {
            'node': node_ovc.instance
        }
        os = service.aysrepo.new('os.ssh.ubuntu', args=args, instance=service.instance, parent=node_ovc)

        args = {
            "image": "jumpscale/g8cockpit",
            'os': os.instance,
            'aysfs': False,
            'ports': '80, 443, 18384'
        }
        docker = service.aysrepo.new('node.docker', args=args, instance="cockpit", parent=os)

        args = {
            'aysfs': True,
            "telegram.token": service.hrd.getStr('telegram.token'),
            "gid": 1,
            "portal.password": service.hrd.getStr('portal.password'),
            "dns.domain": service.hrd.getStr('dns.domain'),
            'node': docker.instance,
            'dns_client': dns_client.instance,
            'oauth.client_secret': service.hrd.getStr("oauth.client_secret"),
            'oauth.client_id': service.hrd.getStr("oauth.client_id"),
            'oauth.organization': service.hrd.getStr("oauth.organization"),
            'oauth.jwt_key': service.hrd.getStr("oauth.jwt_key"),

        }
        cockpit = service.aysrepo.new('os.cockpit', args=args, instance=cockpit_name, parent=docker)
