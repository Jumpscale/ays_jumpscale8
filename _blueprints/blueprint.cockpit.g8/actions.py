from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self, service):
        cockpit_name = service.hrd.getStr('cockpit.name')

        g8_client = service.producers.get('g8client')[0]

        sshkey = service.aysrepo.new('sshkey', instance="main")

        vdcfarm = service.aysrepo.new('vdcfarm', instance="main")

        args = {
            'g8.account': g8_client.hrd.getStr('g8.account'),
            'g8.url': g8_client.hrd.getStr('g8.url'),
            'g8.location': service.hrd.getStr('g8.location'),
            'g8.client.name': g8_client.instance
        }
        vdc = service.aysrepo.new('vdc', args=args, instance=cockpit_name, parent=vdcfarm)

        args = {
            'ports': '80:80, 443:443, 18384:18384, 25:25',
            'sshkey': 'main',
            'os.image': 'Ubuntu 16.04 x64'
        }
        node_ovc = service.aysrepo.new('node.ovc', args=args, instance="cockpitvm", parent=vdc)

        args = {
            'node': node_ovc.instance
        }
        os = service.aysrepo.new('os.ssh.ubuntu', args=args, instance=service.instance, parent=node_ovc)

        args = {
            'dind': service.hrd.getBool('dind', False),
            "dns.domain": service.hrd.getStr('dns.domain'),
            "dns.root": service.hrd.getStr('dns.root'),
            "dns.sshkey": service.hrd.getStr("dns.sshkey"),
            "ays.repo.url": service.hrd.getStr("ays.repo.url"),
            "telegram.token": service.hrd.getStr("telegram.token"),
            "oauth.client_id": service.hrd.getStr("oauth.client_id"),
            "oauth.client_secret": service.hrd.getStr("oauth.client_secret"),
            "oauth.organization": service.hrd.getStr("oauth.organization"),
            "oauth.jwt_key": service.hrd.getStr("oauth.jwt_key"),
            "staging": service.hrd.getBool("staging", False),
        }

        cockpit = service.aysrepo.new('cockpit', args=args, instance=cockpit_name, parent=os)
