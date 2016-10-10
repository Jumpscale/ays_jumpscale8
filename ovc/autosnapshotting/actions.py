def install(job):
    """Take snapshot"""
    service = job.service

    # Get space id from the parent (vdc)
    vdc = service.producers['vdc'][0]

    # Get given space resides in g8client
    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    cl = cl.account_get(vdc.model.data.account)
    space = cl.space_get(vdc.name, vdc.model.data.location)

    for name, machine in space.machines.items():
        machine.create_snapshot()
