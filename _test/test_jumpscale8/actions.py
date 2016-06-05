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
        vdc = service.aysrepo.new('vdc', args=args, instance='cockpit', parent=vdcfarm)

        args = {
            'ports': '80:80, 443:443, 18384:18384',
            'os.image': 'ubuntu 16.04 x64'
        }
        node_ovc = service.aysrepo.new('node.ovc', args=args, instance="ays8test", parent=vdc)

        args = {
            'node': node_ovc.instance,
            'aysfs': False
        }
        os = service.aysrepo.new('os.ssh.ubuntu', args=args, instance=service.instance, parent=node_ovc)

        args = {
            "image": "jumpscale/ubuntu1604",
            'build': True,
            'build.url': 'https://github.com/Jumpscale/dockers',
            'build.path': 'js8/x86_64/ubuntu1604/2_ubuntu1604/',
            'os': os.instance,
            'aysfs': False,
            'ports': '80, 443, 18384'
        }
        docker_devel = service.aysrepo.new('node.docker', args=args, instance="docker_devel", parent=os)


        args = {
            "image": "jumpscale/ubuntu1604",
            'build': True,
            'build.url': 'https://github.com/Jumpscale/dockers',
            'build.path': 'js8/x86_64/ubuntu1604/2_ubuntu1604/',
            'os': os.instance,
            'aysfs': True,
            'ports': '80, 443, 18384'
        }

        docker_sandbox = service.aysrepo.new('node.docker', args=args, instance="docker_sandbox", parent=os)

        args = {
            'node': docker_devel.instance,
            'aysfs': False
        }
        os_docker_devel = service.aysrepo.new('os.ssh.ubuntu', args=args, instance='docker_os', parent=docker_devel)

        # args = {
        #     'node': docker_sandbox.instance,
        #     'aysfs': False
        # }
        # os_docker_sandbox = service.aysrepo.new('os.ssh.ubuntu', args=args, instance='docker_os', parent=docker_sandbox)

        # js8_sandbox = service.aysrepo.new('js8', args={'aysfs': True, 'os': os_docker_sandbox.instance}, instance='js8_sandbox', parent=os_docker_sandbox)

        js8_devel = service.aysrepo.new('js8', args={'aysfs': False, 'os': os_docker_devel.instance}, instance='js8_development', parent=os_docker_devel)

        args = {
            'js8': js8_devel.instance,
            'telegram.token': service.hrd.get('telegram.token'),
            'jwt.key': service.hrd.get('jwt.key'),
            'organization': service.hrd.get('organization')
        }
        cockpit = service.aysrepo.new('cockpit', args=args, instance=service.instance, parent=js8_devel)


        args = {
            'spaces': ['/github/jumpscale/jumpscale_portal8/apps/gridportal/base/Cockpit'],
            'actors': ['/github/jumpscale/jumpscale_portal8/apps/gridportal/base/system__atyourservice/',
                       '/github/jumpscale/jumpscale_portal8/apps/gridportal/base/system__webhooks/',
                       '/github/jumpscale/jumpscale_portal8/apps/gridportal/base/system__gridmanager/'],
        }
        cockpit_portal = service.aysrepo.new('portal', args=args, instance=service.instance, parent=js8_devel)
