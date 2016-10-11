def install(job):
    service = job.service
    # create the docker container based on the data
    os = service.parent
    ports = '-p '.join(service.model.data.ports)
    if ports != '':
        ports = '-p %s' % ports

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

    # find parent node.
    node = None
    for parent in service.parents:
        if parent.model.role == 'node':
            node = parent

    if node is None:
        raise RuntimeError('cannot find parent node')

    docker_ports = []

    for dst_port_spec, host_port_info in ports.items():
        dst_port, _, dst_proto = dst_port_spec.partition('/')
        if host_port_info is None:
            # no bindings
            continue
        host_port = host_port_info[0]['HostPort']
        docker_ports.append('{src}:{dst}'.format(src=host_port, dst=dst_port))

    service.model.data.ipaddress = ipaddress
    service.model.data.ports = docker_ports

    service.saveAll()
