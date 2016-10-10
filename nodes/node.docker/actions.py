def install(job):
    service = job.service
    # create the docker container based on the data
    os = service.parent
    ports = '-p '.join(service.model.data.ports)
    volumes = '-v '.join(service.model.data.volumes)

    # TODO: We will make sure docker is installed on the machine here. But later on
    # we should depend that the machine has docker pre installed
    service.executor.cuisine.systemservices.docker.install()

    cmd = ''
    
    code, out, err = os.executor.cuisine.core.run('docker ps -a --filter name="%(name)s" --format {{.Names}}' % {'name': service.name})
    if code != 0:
        raise RuntimeError('failed to check docker exists: %s' % err)

    if out.strip() == "":  # I am wondering why u inject stuff in stdout.
        # docker doesn't exist
        cmd = 'docker run -d -t --name {name} -p 22 {ports} {volumes} {image}'.format(
            name=service.name,
            ports=ports,
            volumes=volumes,
            image=service.model.data.image,
        )
    else:
        # docker exist, just start it
        cmd = 'docker start {name}'.format(name=service.name)

    code, _, err = os.executor.cuisine.core.run(cmd)
    if code != 0:
        raise RuntimeError('failed to provision/start the docker container: %s' % err)

    # get the ipaddress and ports
    code, inspected, err = os.executor.cuisine.core.run('docker inspect {name}'.format(name=service.name))
    if code != 0:
        raise RuntimeError('failed to inspect docker %s: %s' % (service.name, err))
    inspected = j.data.serializer.json.loads(inspected)
    info = inspected[0]
    ipaddress = info['NetworkSettings']['IPAddress']
    ports = info['NetworkSettings']['Ports']

    docker_ports = []
    for dstPortSpec, hostPortInfo in ports.items():
        dstPort, _, dstProto = dstPortSpec.partition('/')
        if hostPortInfo is None:
            # no bindings
            continue
        hostPort = hostPortInfo[0]['HostPort']
        docker_ports.append('{dst}:{src}'.format(dst=dstPort, src=hostPort))

        # We need to make sure there is a port forward to this hostPort on the node

    service.model.data.currentIPAddress = ipaddress
    service.model.data.currentForwards = docker_ports

    service.saveAll()
