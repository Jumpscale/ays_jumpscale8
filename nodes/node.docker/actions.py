def input(job):
    # support for using node in blueprint to specify the parent.
    # we change it to point to os so it match the requirment of the schema
    args = job.model.args
    if 'node' in args:
        args['os'] = args['node']
        del args['node']
    return args


def init(job):
    service = job.service
    os_actor = service.aysrepo.actorGet('os.ssh.ubuntu')
    os_actor.serviceCreate(service.name, args={'node': service.name, 'sshkey': service.model.data.sshkey})


def install(job):
    service = job.service
    # create the docker container based on the data

    """
    version: '2'
    services:
      mongo:
        image: mongo
        command: "--replSet c0"
        network_mode: "bridge"
        labels:
          SERVICE_TAGS: traefik.enable=false
        ports:
          - "27017"
        volumes:
          - /var/mongo/:/data/
    """
    compose = {
        'version': '2',
        'services': {
            service.name: {
                'image': service.model.data.image,
                'command': service.model.data.cmd,
                'network_mode': 'bridge',
                'ports': list(service.model.data.ports),
                'volumes': list(service.model.data.volumes)
            }
        }
    }

    cuisine = service.executor.cuisine

    base = j.sal.fs.joinPaths('/var', 'dockers', service.name)
    cuisine.core.dir_ensure(base)
    cuisine.core.file_write(
        j.sal.fs.joinPaths(base, 'docker-compose.yml'),
        j.data.serializer.yaml.dumps(compose)
    )

    code, _, err = cuisine.core.run('cd {} && docker-compose up -d'.format(base))
    if code != 0:
        raise RuntimeError('failed to provision docker container: %s' % err)

    code, docker_id, err = cuisine.core.run('cd {} && docker-compose ps -q'.format(base))
    if code != 0:
        raise RuntimeError('failed to get the container id: %s' % err)

    # get the ipaddress and ports
    code, inspected, err = cuisine.core.run('docker inspect {id}'.format(id=docker_id))
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

    service.model.data.ipPrivate = ipaddress
    service.model.data.ipPublic = node.model.data.ipPublic
    service.model.data.sshLogin = 'root'
    service.model.data.sshPassword = 'gig1234'

    service.model.data.ports = docker_ports

    service.saveAll()
