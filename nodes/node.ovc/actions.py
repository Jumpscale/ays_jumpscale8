def install(job):
    service = job.service
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.AYSNotFound("no producer g8client found. cannot continue init of %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name in space.machines:
        # machine already exists
        machine = space.machines[service.name]
    else:
        image_names = [i['name'] for i in space.images]
        if service.model.data.osImage not in image_names:
            raise j.exceptions.NotFound('Image %s not available for vdc %s' % (service.model.data.osImage, vdc.name))

        machine = space.machine_create(name=service.name,
                                       image=service.model.data.osImage,
                                       memsize=service.model.data.memory,
                                       disksize=service.model.data.bootdiskSize)

    service.model.data.machineId = machine.id
    service.model.data.ipPublic = machine.space.model['publicipaddress']
    ip, vm_info = machine.get_machine_ip()
    service.model.data.ipPrivate = ip
    service.model.data.sshLogin = vm_info['accounts'][0]['login']
    service.model.data.sshPassword = vm_info['accounts'][0]['password']

    for i, port in enumerate(service.model.data.ports):
        ss = port.split(':')
        if len(ss) == 2:
            public_port, local_port = ss
        else:
            local_port = port
            public_port = None

        public, local = machine.create_portforwarding(publicport=public_port, localport=local_port, protocol='tcp')
        service.model.data.ports[i] = "%s:%s" % (public, local)
    if 'sshkey' not in service.producers:
        raise j.exceptions.AYSNotFound("No sshkey service consumed. please consume an sshkey service")

    sshkey = service.producers['sshkey'][0]
    service.logger.info("authorize ssh key to machine")
    node = service

    # Looking in the parents chain is needed when we have nested nodes (like a docker node on top of an ovc node)
    # we need to find all the ports forwarding chain to reach the inner most node.
    ssh_port = '22'

    for port in service.model.data.ports:
        src, _, dst = port.partition(':')
        if ssh_port == dst:
            ssh_port = src
            break

    service.model.data.sshPort = int(ssh_port)

    sshkey = service.producers['sshkey'][0]
    key_path = j.sal.fs.joinPaths(sshkey.path, 'id_rsa')
    password = node.model.data.sshPassword if node.model.data.sshPassword != '' else None

    # used the login/password information from the node to first connect to the node and then authorize the sshkey for root
    executor = j.tools.executor.getSSHBased(addr=node.model.data.ipPublic, port=service.model.data.sshPort,
                                            login=node.model.data.sshLogin, passwd=password,
                                            allow_agent=True, look_for_keys=True, timeout=5, usecache=False,
                                            passphrase=None, key_filename=key_path)
    executor.cuisine.ssh.authorize("root", sshkey.model.data.keyPub)

    cuisine = executor.cuisine

    devicesmap = {}  # diskname -> devicename
    seendevices = []  # only the ones with mountpoint is null
    # Add disks to machine
    for data_disk in service.producers.get('disk', []):
        disk_args = data_disk.model.data
        disk_id = machine.add_disk(name=data_disk.model.dbobj.name,
                                   description=disk_args.description,
                                   size=disk_args.size,
                                   type=disk_args.type.upper())
        rc, out, err = cuisine.core.run("lsblk -J", die=False)

        jsonout = j.data.serializer.json.loads(out)
        devices = [x for x in jsonout['blockdevices'] if x['mountpoint'] is None and x['type'] == 'disk'] # should be only 1

        for dv in devices:
            if 'children' in dv:
                continue
            if dv['name'] not in seendevices:
                data_disk.model.data.devicename = dv['name']
                data_disk.saveAll()
                devicesmap[data_disk.model.dbobj.name] = dv['name']
                seendevices.append(dv['name'])


        machine.disk_limit_io(disk_id, disk_args.maxIOPS)  #COMMENTED BECAUSE OF GIG

    service.saveAll()


def open_port(job):
    """
    Open port in the firewall by creating port forward
    if public_port is None, auto select available port
    Return the public port assigned
    """
    requested_port = job.model.args['requested_port']
    public_port = job.model.args.get('public_port', None)

    service = job.service
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.AYSNotFound("no producer g8client found. cannot continue init of %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name in space.machines:
        # machine already exists
        machine = space.machines[service.name]
    else:
        raise RuntimeError('machine not found')

    # check if already open, if yes return public port
    spaceport = None
    for pf in machine.portforwardings:
        if pf['localPort'] == requested_port:
            spaceport = pf['publicPort']
            break

    ports = set(service.model.data.ports)

    if spaceport is None:
        if public_port is None:
            # reach that point, the port is not forwarded yet
            unavailable_ports = [int(portinfo['publicPort']) for portinfo in machine.space.portforwardings]
            spaceport = 2200
            while True:
                if spaceport not in unavailable_ports:
                    break
                else:
                    spaceport += 1
        else:
            spaceport = public_port

        machine.create_portforwarding(spaceport, requested_port)

    ports.add("%s:%s" % (spaceport, requested_port))
    service.model.data.ports = list(ports)

    service.saveAll()

    return spaceport


def uninstall(job):
    service = job.service
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.RuntimeError("no producer g8client found. cannot continue init of %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name not in space.machines:
        return
    machine = space.machines[service.name]
    machine.delete()


def start(job):
    service = job.service
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.RuntimeError("no producer g8client found. cannot continue init of %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name not in space.machines:
        return
    machine = space.machines[service.name]
    machine.start()


def stop(job):
    service = job.service
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.RuntimeError("no producer g8client found. cannot continue init of %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name not in space.machines:
        return
    machine = space.machines[service.name]
    machine.stop()


def restart(job):
    service = job.service
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.RuntimeError("no producer g8client found. cannot continue init of %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name not in space.machines:
        return
    machine = space.machines[service.name]
    machine.restart()


def mail(job):
    print('hello world')
