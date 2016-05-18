from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self, service):
        
        args=service.args

        if 'g8.url' in args:
            #will use existing one if it exists
            service.aysrepo.new('g8client', args=args, instance="main")

        # args = {
        #     'url': 'https://dns1.aydo.com/etcd',
        #     'login': '$(dns.login)',
        #     'password': '$(dns.password)'
        # }
        # dns_client = service.aysrepo.new('dns_client', args=args, instance="main")


        sshkey = service.aysrepo.new('sshkey', instance="main")

        if "vdc.farm" in args:
            farminstance=args["vdc.farm"]
        else:
            farminstance="main"

        if "vdc.name" in args:
            vdcname=args["vdc.name"]
        else:
            vdcname="main"

        vdcfarm = service.aysrepo.new('vdcfarm', instance=farminstance)

        vdc = service.aysrepo.new('vdc',instance=vdcname, parent=vdcfarm)

        from IPython import embed
        print ("DEBUG NOW blueprint os")
        embed()
        

        args = {'ports': '80:80, 443:443, 18384:18384'}
        node_ovc = service.aysrepo.new('node.ovc', args=args, instance="cockpitvm", parent=vdc)

        args = {'node': node_ovc.instance}
        os = service.aysrepo.new('os.ssh.ubuntu', args=args, instance=service.instance, parent=node_ovc)

