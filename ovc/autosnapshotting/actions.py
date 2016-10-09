def install(job):
    """Take snapshot"""
    service = job.service

    # Get space id from the parent (vdc)
    vdc = service.producers['vdc'][0]

    # Get machine from spaces residing in g8client
    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    cl = cl.account_get(vdc.model.data.account)
    spaces = cl.spaces

    for space in spaces:
        for name, machine in space.machines.items():
            machine.create_snapshot()
