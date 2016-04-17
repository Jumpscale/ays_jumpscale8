from JumpScale import j


class Actions():

    def init(self):

        # if self.service.hrd.getBool('shellinabox'):
        #     shellinabox = j.atyourservice.new(instance=self.service.instance, consume=self.service)
        return True

    def install(self):
        sshkey = self.service.getProducers('sshkey')[0]
        pubkey = sshkey.hrd.get('key.pub')
        image = self.service.hrd.getStr('image')
        if 'node' in self.service.parent.producers:
            host_node = self.service.parent.producers['node'][0]
        else:
            raise j.exceptions.NotFound("Can't find host node of this service %s" % self.service)

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

        docker_ports = self.service.hrd.getList('ports')
        pf_creation = []
        for docker_port in docker_ports:
            p = get_host_port(docker_port)
            if p is None:
                pf_creation.append("%s:%s" % (docker_port, docker_port))
            else:
                pf_creation.append("%s:%s" % (p, docker_port))

        if self.service.parent.hrd.getBool('aysfs'):
            aysfs = self.service.hrd.getBool('aysfs')
            connection_str = self.service.executor.cuisine.docker.ubuntu(name=self.service.instance, image=image,
                                                        pubkey=pubkey, aydofs=aysfs, ports=' '.join(pf_creation))
        else:
            # js not available
            connection_str = self.service.executor.cuisine.core.run("docker run -t jumpscale/ubuntu1510")
        # self.service.executor.cuisine.docker.enableSSH(connection_str)

        local_port = connection_str.split(':')[1]
        public_port = host_node.actions.open_port(local_port)

        self.service.hrd.set('docker.sshport', public_port)
        self.service.hrd.set('node.addr', self.service.executor.addr)
        self.service.hrd.set('portforwards', pf_creation)

        # use proper logger
        print("OUT: Docker %s deployed." % self.service.instance)
        print("OUT: IP %s" % self.service.executor.addr)
        print("OUT: SSH port %s" % public_port)
