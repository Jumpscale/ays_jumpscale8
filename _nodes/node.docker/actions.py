from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self, service):

        # if service.hrd.getBool('shellinabox'):
        #     shellinabox = service.aysrepo.new(instance=service.instance, consume=service)
        return True

    def install(self, service):
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
                if ":" in docker_port:
                    p, docker_port = docker_port.split(":")
                    pf_creation.append("%s:%s" % (p, docker_port))
                else:
                    pf_creation.append("%s" % (docker_port))
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
                private, public = pf.split(":")
                if docker_port == private:
                    return private
            return None

        docker_ports = service.hrd.getList('ports')
        pf_creation = _pf_map(docker_ports)

        dind = service.hrd.getBool('dind', False)
        volumes = None if not dind else '/var/run/docker.sock:/var/run/docker.sock'

        if service.parent.hrd.getBool('aysfs'): # TODO: *1 not right !
            aysfs = service.hrd.getBool('aysfs')
            pfs = ' '.join(pf_creation)

            connection_str = service.executor.cuisine.docker.ubuntu(name=service.instance, image=image,
                                                        pubkey=pubkey, aydofs=aysfs, ports=pfs, volumes=volumes)
            local_port = connection_str.split(':')[1]
            public_port = host_node.actions.open_port(host_node, local_port)
        else:
            # js not available
            pfs = '-p %s' % (' -p '.join(pf_creation)) if pf_creation else ''
            pfs = ' -p 22 %s ' % pfs
            restart = service.hrd.getBool('restart', False)
            if not restart:
                restart = ''
            else:
                restart = '--restart=always'
            _, out, _ = service.executor.cuisine.core.run('docker ps -a -f name="\\b%s\\b" -q' % service.instance, profile=True)
            if not out:
                if service.hrd.getBool('build'):
                    dest = j.sal.fs.joinPaths(service.executor.cuisine.core.dir_paths['varDir'], j.sal.fs.getBaseName(service.hrd.get('build.url')))
                    service.executor.cuisine.git.pullRepo(service.hrd.get('build.url'), dest)
                    service.executor.cuisine.core.run('cd %s; docker build  --tag="%s"  %s' % (dest, image, service.hrd.get('build.path')))
                volumes = '-v %s' % volumes if volumes else ''
                service.executor.cuisine.core.run("docker run -d %s -t %s --name %s --privileged=true %s %s " % (restart, pfs, service.instance, volumes, image), profile=True)
            else:
                service.executor.cuisine.core.run("docker start %s" % out, profile=True)
            # add sshkey
            service.executor.cuisine.core.run('docker exec %s mkdir -p /root/.ssh' % (service.instance), profile=True)
            service.executor.cuisine.core.run('docker exec %s touch /root/.ssh/authorized_keys' % (service.instance), profile=True)
            service.executor.cuisine.core.run('docker exec %s /bin/bash -c \'"\'echo \"\'\"%s\"\'\" >> /root/.ssh/authorized_keys\'"\'' % (service.instance, pubkey), profile=True)

            #get all portforward from container to host
            pf_creation = []
            pf_lines = service.executor.cuisine.core.run("docker port %s" % service.instance)[1].splitlines()
            for portf in pf_lines:
                tmp = portf.split('/')
                if tmp[0] == "22":
                    vm_port = tmp[1].split(":")[1]
                    continue
                pf_creation.append("%s:%s" % (tmp[0], tmp[1].split(":")[1]))

            spaceport = []
            for item in pf_creation:
                docker_port, host_port = item.split(":")
                if not get_host_port(docker_port):
                    spaceport.append("%s:%s" % (host_node.actions.open_port(host_node, host_port, docker_port), docker_port))
            public_port = host_node.actions.open_port(host_node, vm_port)

            # service.executor.cuisine.core.run('docker exec %s /bin/bash -c "cat >> /root/.ssh/authorized_keys <<EOF\n%s\nEOF"' % (service.instance, pubkey))

        # service.executor.cuisine.docker.enableSSH(connection_str)
        addr = 0
        if service.hrd.getBool('docker.local', False):
            public_port = 22
            _, addr, _ = service.executor.cuisine.core.run("docker inspect --format '{{ .NetworkSettings.IPAddress }}' %s" % service.instance)

        service.hrd.set('docker.sshport', public_port)

        addr = addr or service.executor.addr
        service.hrd.set('node.addr', addr)
        service.hrd.set('portforwards', pf_creation)

        for child in service.children:
            child.hrd.set("ssh.addr", addr)
            child.hrd.set("ssh.port", public_port)

        # use proper logger
        print("OUT: Docker %s deployed." % service.instance)
        print("OUT: IP %s" % addr)
        print("OUT: SSH port %s" % public_port)

    def open_port(self, service, requested_port, public_port=None):
        if 'node' in service.parent.producers:
            host_node = service.parent.producers['node'][0]
            return host_node.actions.open_port(host_node, requested_port, public_port)
        return requested_port
