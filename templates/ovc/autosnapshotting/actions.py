def install(job):
    """Configure recurring actions"""

    service = job.service

    snapshot_action = service.model.actions['snapshot']
    snapshot_action.period = j.data.types.duration.convertToSeconds(service.model.data.snapshotInterval)
    snapshot_action.log = True
    snapshot_action.lastRun = 0

    snapshot_action = service.model.actions['cleanup']
    snapshot_action.period = j.data.types.duration.convertToSeconds(service.model.data.cleanupInterval)
    snapshot_action.log = True
    snapshot_action.lastRun = 0

    service.saveAll()


def snapshot (job):
    from dateutil import parser
    import datetime
    import time
    service = job.service
    START_DATE = parser.parse(service.model.data.startDate) if service.model.data.endDate != "" else ""
    END_DATE = parser.parse(service.model.data.endDate) if service.model.data.endDate != "" else ""
    start_date_valid = START_DATE == "" or START_DATE < datetime.datetime.now()
    end_date_valid = END_DATE == "" or END_DATE > datetime.datetime.now()
    vdc = service.producers["vdc"][0]
    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    cl = cl.account_get(vdc.model.data.account)
    space = None
    try:
        space = cl.space_get(vdc.name, vdc.model.data.location, create=False)
    except:
        return
    now = int(time.time())
    period = j.data.types.duration.convertToSeconds(service.model.data.snapshotInterval)
    if not (start_date_valid and end_date_valid):
        return
    for name, machine in space.machines.items():
        for snapshot in machine.list_snapshots():
            delta = now - snapshot['epoch']
            if delta < period:
                break
            machine.create_snapshot(name='auto_snapshot')


def cleanup(job):
    """Removing snapshot that's lifetime exceeds the given retention"""
    import time

    service = job.service
    RETENTION = j.data.types.duration.convertToSeconds(service.model.data.retention)

    # Get spaces id from the parent (vdc)
    vdc = service.producers["vdc"][0]
    # Get given space resides in g8client
    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    cl = cl.account_get(vdc.model.data.account)
    space = cl.space_get(vdc.name, vdc.model.data.location)

    now = int(time.time())
    for name, machine in space.machines.items():
        for snapshot in machine.list_snapshots():
            # Get the delta time in seconds
            delta = now - snapshot['epoch']
            if delta >= RETENTION:
                machine.delete_snapshot(snapshot['epoch'])
