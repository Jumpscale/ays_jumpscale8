from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self, service):
        args = {'g8.url': service.hrd.getStr('g8.url'),
                'g8.login': service.hrd.getStr('g8.login'),
                'g8.password': service.hrd.getStr('g8.password')}
        g8_client = service.aysrepo.new('g8client', args=args, instance="main")

        sshkey = service.aysrepo.new('sshkey', instance="main")

        vdcfarm = service.aysrepo.new('vdcfarm', instance="main")

        args = {
            'g8.account': service.hrd.getStr('g8.account'),
            'g8.url': service.hrd.getStr('g8.url'),
            'g8.client.name': g8_client.instance
        }
        vdc = service.aysrepo.new('vdc', args=args, instance='js8', parent=vdcfarm)

        args = {
            'ports': '80:80, 443:443, 18384:18384',
            'os.image': 'Ubuntu 16.04 x64'
        }
        node_ovc = service.aysrepo.new('node.ovc', args=args, instance="ays8test", parent=vdc)

        args = {
            'node': node_ovc.instance,
            'aysfs': False
        }
        os = service.aysrepo.new('os.ssh.ubuntu', args=args, instance=service.instance, parent=node_ovc)

        args = {
            "image": "ubuntu:xenial",
            'os': os.instance,
            'aysfs': False,
            'ports': '80, 443, 18384'
        }
        docker = service.aysrepo.new('node.docker', args=args, instance="js8_devel", parent=os)

        args = {
            'node': docker.instance,
            'aysfs': False
        }
        os_docker = service.aysrepo.new('os.ssh.ubuntu', args=args, instance='docker_os', parent=docker)

        js8 = service.aysrepo.new('js8', args={'aysfs': False, 'os': os_docker.instance}, parent=os_docker)
