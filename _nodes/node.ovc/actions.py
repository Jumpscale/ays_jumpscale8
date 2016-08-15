from JumpScale import j


class Actions(ActionsBaseMgmt):

    def getMachine(self, service):

        client = service.parent.actions.getClient(service.parent)

        vdcobj = service.parent

        account = client.account_get(vdcobj.hrd.get("g8.account"))

        spacename = service.parent.instance

        location = client.locations[0]['name'] if not vdcobj.hrd.get('g8.location', None) else vdcobj.hrd.get('g8.location')
        space = account.space_get(spacename, location=location)
        if service.instance in space.machines:
            return space.machines[service.instance]
        else:
            datadisks = [int(j.data.tags.getObject(disk).tagGet('size')) for disk in service.hrd.getList('datadisks')]
            machine = space.machine_create(name=service.instance,
                                           image=service.hrd.getStr('os.image'),
                                           memsize=service.hrd.getInt('os.size'),
                                           disksize=service.hrd.getInt('disk.size'),
                                           datadisks=datadisks)
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
        sshkey = service.producers.get('sshkey')[0]
        executor = j.tools.executor.getSSHBased(service.hrd.get("publicip"), service.hrd.getInt("sshport"), 'root', pushkey=sshkey.hrd.get('key.path'))

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

        portforwards = dict()
        for port in service.hrd.getList('ports'):
            ss = port.split(':')
            if len(ss) == 2:
                portforwards[ss[1]] = ss[0]
            else:
                portforwards[ss] = None

        sshport = portforwards.get('22', None)
        executor = machine.get_ssh_connection(sshport)
        if not service.hrd.get('publicip', ''):
            service.hrd.set('publicip', machine.space.model['publicipaddress'])
            service.hrd.set('privateip', machine.get_machine_ip()[0])
            service.hrd.set('sshport', executor.port)
            if len(service.producers['sshkey']) >= 1:
                sshkey = service.producers['sshkey'][0]
                executor.cuisine.core.hostname = service.instance
                executor.cuisine.ssh.authorize('root', sshkey.hrd.get('key.pub'))

        for child in service.children:
            child.hrd.set("ssh.addr", service.hrd.get("publicip"))
            child.hrd.set("private.addr", service.hrd.get("privateip"))
            child.hrd.set("ssh.port", service.hrd.get("sshport"))

        for requested_port, public_port in portforwards.items():
            self.open_port(service, requested_port=requested_port, public_port=public_port)

    def uninstall(self, service):
        if service.hrd.get('machineid', ''):
            machine = self.getMachine(service)
            machine.delete()
