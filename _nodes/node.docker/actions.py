from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self):

        # if service.hrd.getBool('shellinabox'):
        #     shellinabox = service.aysrepo.new(instance=service.instance, consume=service)
        return True

    def install(self):
        sshkey = service.getProducers('sshkey')[0]
        pubkey = sshkey.hrd.get('key.pub')
        image = service.hrd.getStr('image')
        if 'node' in service.parent.producers:
            host_node = service.parent.producers['node'][0]
        else:
            raise j.exceptions.NotFound("Can't find host node of this service %s" % service)

        def _pf_map(docker_ports):
            pf_creation = []
            for docker_port in docker_ports:
                p = get_host_port(docker_port)
                if p is None:
                    pf_creation.append("%s:%s" % (docker_port, docker_port))
                else:
                    pf_creation.append("%s:%s" % (p, docker_port))
            return pf_creation

        def get_host_port(docker_port):
            """
            find the private port the docker need to use to forward to public
            e.g:
                the docker need to expose its port 80.
                He needs to know what port the host_node forward to port 80 to the public internet
                internet  80|5000  host_node   5000|80  docker
                in this example, the docker need to do a portforwards from 5000 to 80
                to have its port 80 expose to internet.
            """
            host_pf = host_node.hrd.getList("portforwards", [])
            for pf in host_pf:
                public, private = pf.split(":")
                if docker_port == public:
                    return private
            return None

        docker_ports = service.hrd.getList('ports')
        pf_creation = _pf_map(docker_ports)

        if service.parent.hrd.getBool('aysfs'): #@todo (*1*) not right !
            aysfs = service.hrd.getBool('aysfs')
            pfs = ' '.join(pf_creation)
            connection_str = service.executor.cuisine.docker.ubuntu(name=service.instance, image=image,
                                                        pubkey=pubkey, aydofs=aysfs, ports=pfs)
            local_port = connection_str.split(':')[1]
            public_port = host_node.actions.open_port(local_port)
        else:
            # js not available
            pfs = ' -p '.join(pf_creation)
            out = service.executor.cuisine.core.run('docker ps -f name=%s -q' % service.instance)
            if not out:
                service.executor.cuisine.core.run("docker run -d -t -p %s -p 22 --name %s --privileged=true %s " % (pfs, service.instance, image))
            vm_port = service.executor.cuisine.core.run("docker port %s 22" % service.instance).split(':')[1]
            public_port = host_node.actions.open_port(vm_port)
            # add sshkey
            service.executor.cuisine.core.run('docker exec %s touch /root/.ssh/authorized_keys' % (service.instance))
            service.executor.cuisine.core.run('docker exec %s /bin/bash -c "echo \'%s\' >> /root/.ssh/authorized_keys"' % (service.instance, pubkey))
            # service.executor.cuisine.core.run('docker exec %s /bin/bash -c "cat >> /root/.ssh/authorized_keys <<EOF\n%s\nEOF"' % (service.instance, pubkey))

        # service.executor.cuisine.docker.enableSSH(connection_str)

        service.hrd.set('docker.sshport', public_port)
        service.hrd.set('node.addr', service.executor.addr)
        service.hrd.set('portforwards', pf_creation)

        for child in service.children:
            child.hrd.set("ssh.addr", service.executor.addr)
            child.hrd.set("ssh.port", public_port)

        # use proper logger
        print("OUT: Docker %s deployed." % service.instance)
        print("OUT: IP %s" % service.executor.addr)
        print("OUT: SSH port %s" % public_port)
