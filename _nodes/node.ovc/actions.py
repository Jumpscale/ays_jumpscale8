from JumpScale import j


class Actions(ActionsBaseMgmt):

    def getMachine(self, service):

        client = service.parent.actions.getClient(service.parent)

        vdcobj = service.parent

        account = client.account_get(vdcobj.hrd.get("g8.account"))

        spacename = service.parent.instance

        space = account.space_get(spacename, location=client.locations[0]['name'])
        if service.instance in space.machines:
            return space.machines[service.instance]
        else:
            machine = space.machine_create(name=service.instance,
                                           image=service.hrd.getStr('os.image'),
                                           memsize=service.hrd.getInt('os.size'),
                                           disksize=service.hrd.getInt('disk.size'),
                                           datadisks=service.hrd.getList('datadisks', []))
            return machine

    def open_port(self, service, requested_port, public_port=None):
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
        machine = self.getMachine(service)
        executor = j.tools.executor.getSSHBased(service.hrd.get("publicip"), service.hrd.getInt("sshport"), 'root')

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

        pf = service.hrd.getList('portforwards', [])
        pf.append("%s:%s" % (spaceport, requested_port))
        service.hrd.set('portforwards', pf)

        return spaceport

    def install(self, service):
        machine = self.getMachine(service)
        service.hrd.set('machineid', machine.id)

        executor = machine.get_ssh_connection()
        if not service.hrd.get('publicip', ''):
            service.hrd.set('publicip', machine.space.model['publicipaddress'])
            service.hrd.set('sshport', executor.port)
            if len(service.producers['sshkey']) >= 1:
                sshkey = service.producers['sshkey'][0]
                executor.cuisine.core.hostname = service.instance
                executor.cuisine.ssh.authorize('root', sshkey.hrd.get('key.pub'))

        for child in service.children:
            child.hrd.set("ssh.addr", service.hrd.get("publicip"))
            child.hrd.set("ssh.port", service.hrd.get("sshport"))

        for port in service.hrd.getList('ports'):
            ss = port.split(':')
            if len(ss) == 2:
                self.open_port(service, requested_port=ss[1], public_port=ss[0])
            else:
                self.open_port(service, requested_port=port)


    def uninstall(self, service):
        if service.hrd.get('machineid', ''):
            machine = self.getMachine(service)
            machine.delete()
