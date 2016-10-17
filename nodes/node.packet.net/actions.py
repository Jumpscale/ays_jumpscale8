def install(job):
    import time
    import packet

    service = job.service

    # create a new packet
    # make sure our sshkey gets there
    sshkey = service.producers.get('sshkey')[0]
    packetclient = service.producers.get('packetnet_client')[0]
    client = packet.Manager(packetclient.model.data.token)

    hostname = service.model.data.deviceName

    project_name = service.model.data.projectName
    project_ids = [project.id for project in client.list_projects() if project.name == project_name]
    if not project_ids:
        raise RuntimeError('No projects found with name %s' % project_name)
    project_id = project_ids[0]

    key_pub = sshkey.model.data.keyPub
    key_labels = [key.label for key in client.list_ssh_keys()]
    key_keys = [key.key for key in client.list_ssh_keys()]
    if key_pub not in key_keys:
        i = 1
        key_label = "%s-%s" % (service.name, i)
        while not key_label or key_label in key_labels:
            key_label = "%s-%s" % (service.name, i)
            i += 1
        client.create_ssh_key(key_label, key_pub)

    project_devices = {device.hostname: device for device in client.list_devices(project_id)}
    if hostname not in project_devices:
        plan_type = service.model.data.planType
        plan_ids = [plan.id for plan in client.list_plans() if plan.name == plan_type]
        if not plan_ids:
            raise RuntimeError('No plans found with name %s' % plan_type)
        plan_id = plan_ids[0]

        operating_system_name = service.model.data.deviceOs
        operating_systems = [operating_system.slug for operating_system in client.list_operating_systems() if operating_system.name == operating_system_name]
        if not operating_systems:
            raise RuntimeError('No operating_systems found with name %s' % operating_system_name)
        operating_system = operating_systems[0]

        facility_id = client.list_facilities()[0].id

        device = client.create_device(project_id=project_id, hostname=hostname, plan=plan_id, facility=facility_id, operating_system=operating_system)
    else:
        device = project_devices[hostname]

    timeout_start = time.time()
    timeout = 900
    while time.time() < timeout_start + timeout and device.state != 'active':
        time.sleep(5)
        device = client.get_device(device.id)

    if device.state != 'active':
        raise RuntimeError('Too long to provision')

    service.model.data.deviceId = device.id
    service.model.data.sshLogin = device.user

    ip = [netinfo['address'] for netinfo in device.ip_addresses if netinfo['public'] and netinfo['address_family'] == 4]
    service.model.data.ipPublic = ip[0]
    service.model.data.ports = ['22:22']

    service.saveAll()


def uninstall(job):
    import packet
    service = job.service
    packetclient = service.producers.get('packetnet_client')[0]
    client = packet.Manager(packetclient.model.data.token)

    device_id = service.model.data.deviceId
    if device_id is None or device_id == '':
        raise j.exceptions.NotFound("device id not know, node probably not installed")
    device = client.get_device(device_id)
    device.delete()