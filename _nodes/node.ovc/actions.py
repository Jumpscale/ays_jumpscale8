from JumpScale import j


class Actions(ActionsBaseMgmt):

    def getMachine(self):

        client = self.service.parent.actions.getClient()

        vdcobj = self.service.parent

        account = client.account_get(vdcobj.hrd.get("g8.account"))

        spacename = self.service.parent.instance

        space = account.space_get(spacename, location=client.locations[0]['name'])
        if self.service.instance in space.machines:
            return space.machines[self.service.instance]
        else:
            machine = space.machine_create(name=self.service.instance,
                                           image=self.service.hrd.get('os.image'),
                                           memsize=int(self.service.hrd.get('os.size')))
            return machine

    def open_port(self, requested_port, public_port=None):
        """
        Open port in the firewall by creating port forward
        if public_port is None, auto select available port
        Return the public port assigned
        """
        def _get_free_port(unavailable_ports):
            candidate = 2200
            while True:
                if candidate not in unavailable_ports:
                    return candidate
                else:
                    candidate += 1
        machine = self.service.actions.getMachine()
        executor = j.tools.executor.getSSHBased(self.service.hrd.get("publicip"), self.service.hrd.getInt("sshport"), 'root')

        # check if already open, if yes return public port
        spaceport = None
        for pf in machine.portforwardings:
            if pf['localPort'] == requested_port:
                spaceport = pf['publicPort']
                break

        if spaceport is None:
            if public_port is None:
                # reach that point, the port is not forwarded yet
                spaceport = _get_free_port([int(portinfo['publicPort']) for portinfo in machine.space.portforwardings])
            else:
                spaceport = public_port

            machine.create_portforwarding(spaceport, requested_port)

        pf = self.service.hrd.getList('portforwards', [])
        pf.append("%s:%s" % (spaceport, requested_port))
        self.service.hrd.set('portforwards', pf)

        return spaceport

    def install(self):
        machine = self.service.actions.getMachine()
        self.service.hrd.set('machineid', machine.id)

        executor = machine.get_ssh_connection()
        if not self.service.hrd.get('publicip', ''):
            self.service.hrd.set('publicip', machine.space.model['publicipaddress'])
            self.service.hrd.set('sshport', executor.port)
            if len(self.service.producers['sshkey']) >= 1:
                sshkey = self.service.producers['sshkey'][0]
                executor.cuisine.core.hostname = self.service.instance
                executor.cuisine.ssh.authorize('root', sshkey.hrd.get('key.pub'))

        for child in self.service.children:
            child.hrd.set("ssh.addr", self.service.hrd.get("publicip"))
            child.hrd.set("ssh.port", self.service.hrd.get("sshport"))

        for port in self.service.hrd.getList('ports'):
            ss = port.split(':')
            if len(ss) == 2:
                self.service.actions.open_port(requested_port=ss[1], public_port=ss[0])
            else:
                self.service.actions.open_port(requested_port=port)


    def uninstall(self):
        if self.service.hrd.get('machineid', ''):
            machine = self.service.actions.getMachine()
            machine.delete()
