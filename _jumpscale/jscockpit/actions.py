from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self, service):
        os = service.parent
        args = {
            'key.path': service.hrd.getStr('dns.sshkey')
        }
        sshkey_dns = service.aysrepo.new('sshkey', args=args, instance="dns")

        dns_clients = []
        for i in range(1, 4):
            args = {
                'addr': 'dns%d.aydo.com' % i,
                'port': 32768,
                'login': service.hrd.getStr('dns.login'),
                'password': service.hrd.getStr('dns.password'),
                'sshkey': sshkey_dns.instance
            }
            dns_clients.append(service.aysrepo.new('dns_client', args=args, instance="main%d" % i))

        args = {
            "image": "jumpscale/g8cockpit",
            'os': os.instance,
            'aysfs': False,
            'ports': '80, 443, 18384',
            'sshkey': 'main'
        }
        docker = service.aysrepo.new('node.docker', args=args, instance="cockpit", parent=os)

        args = {
            'aysfs': True,
            "telegram.token": service.hrd.getStr('telegram.token'),
            "gid": 1,
            "portal.password": service.hrd.getStr('portal.password'),
            "dns.domain": service.hrd.getStr('dns.domain'),
            'node': docker.instance,
            'dns_client': [s.instance for s in dns_clients],
            'oauth.client_secret': service.hrd.getStr("oauth.client_secret"),
            'oauth.client_id': service.hrd.getStr("oauth.client_id"),
            'oauth.organization': service.hrd.getStr("oauth.organization"),
            'oauth.jwt_key': service.hrd.getStr("oauth.jwt_key"),

        }
        cockpit = service.aysrepo.new('os.cockpit', args=args, instance=service.instance, parent=docker)
        print (cockpit)
