from JumpScale import j


class Actions(ActionsBaseMgmt):
    def init(self, service):
        pass

    def install(self, service):
        import time
        # create a new packet
        # make sure our sshkey gets there
        sshkey = service.producers.get('sshkey')[0]
        packetclient = service.producers.get('packetclient')[0]
        client = packetclient.actions.get_client(packetclient)

        hostname = service.hrd.get('packet.device.name')

        project_name = service.hrd.get('packet.project.name')
        project_ids = [project.id for project in client.list_projects() if project.name == project_name]
        if not project_ids:
            raise RuntimeError('No projects found with name %s' % project_name)
        project_id = project_ids[0]

        if service.instance not in [key.label for key in client.list_ssh_keys()]:
            client.create_ssh_key(service.instance, sshkey.hrd.get('key.pub'))

        project_devices = {device.hostname: device for device in client.list_devices(project_id)}
        if hostname not in project_devices:
            plan_type = service.hrd.get('packet.plan.type')
            plan_ids = [plan.id for plan in client.list_plans() if plan.name == plan_type]
            if not plan_ids:
                raise RuntimeError('No plans found with name %s' % plan_type)
            plan_id = plan_ids[0]

            operating_system_name = service.hrd.get('packet.device.os')
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

        ip = [netinfo['address'] for netinfo in device.ip_addresses if netinfo['public'] and netinfo['address_family'] == 4]
        service.hrd.set("publicip", ip[0])
        service.hrd.set("sshport", 22)
        for child in service.children:
            child.hrd.set("ssh.addr", service.hrd.get("publicip"))
            child.hrd.set("ssh.port", service.hrd.get("sshport"))

    def open_port(self, service, requested_port, public_port=None):
        return requested_port
