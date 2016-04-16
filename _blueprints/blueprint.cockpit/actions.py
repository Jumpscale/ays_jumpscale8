from JumpScale import j


class Actions():

    def init(self):
        args = {'g8.url': "$(g8.url)",
                'g8.login': "$(g8.login)",
                'g8.password': "$(g8.password)"}

        account="$(g8.account)"
        if account.strip()=="":
            account="$(g8.login)"

        j.atyourservice.new('g8client', args=args, instance="main")

        args = {
            'url': 'https://dns1.aydo.com/etcd',
            'login': '$(dns.login)',
            'password': '$(dns.password)'
        }
        dns_client = j.atyourservice.new('dns_client', args=args, instance="main")

        sshkey = j.atyourservice.new('sshkey', instance="main")

        vdcfarm = j.atyourservice.new('vdcfarm', instance="main")

        vdc = j.atyourservice.new('vdc', args={'g8.account': account},instance="$(cockpit.name)", parent=vdcfarm)

        args = {'ports': '80:80, 443:443, 18384:18384'}
        node_ovc = j.atyourservice.new('node.ovc', args=args, instance="cockpitvm", parent=vdc)

        args = {'node': node_ovc.instance}
        os = j.atyourservice.new('os.ssh.ubuntu', args=args, instance=self.service.instance, parent=node_ovc)

        args = {
            "image": "jumpscale/g8cockpit",
            'os': os.instance,
            'aysfs': False,
            'ports': '80, 443, 18384'
        }
        docker = j.atyourservice.new('node.docker', args=args, instance="cockpit", parent=os)

        args = {
            "telegram.token": self.service.hrd.getStr('telegram.token'),
            "gid": 1,
            "portal.password": "$(portal.password)",
            "dns.domain": "$(cockpit.name)",
            'node': docker.instance,
            'dns_client': dns_client.instance
        }
        cockpit = j.atyourservice.new('os.cockpit', args=args, instance="$(cockpit.name)", parent=docker)
