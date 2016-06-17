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
            'g8.client.name': g8_client.instance
        }
        vdc = service.aysrepo.new('vdc', args=args, instance=cockpit_name, parent=vdcfarm)

        args = {
            'ports': '80:80, 443:443, 18384:18384',
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
            "dns.domain": service.hrd.get('dns.domain'),
            "dns.sshkey": service.hrd.get("dns.sshkey"),
            "ays.repo.url": service.hrd.get("ays.repo.url"),
        }

        cockpit = service.aysrepo.new('cockpit', args=args, instance=cockpit_name, parent=os)
