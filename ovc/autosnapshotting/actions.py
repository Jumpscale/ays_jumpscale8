def install(job):
    """Configure recurring actions"""

    service = job.service

    RECURRING_ACTION_COUNT = 2
    service.model.dbobj.init("recurringActions", RECURRING_ACTION_COUNT)

    recurring = service.model.dbobj.recurringActions[0]
    recurring.action = "snapshot"
    recurring.period = j.data.types.duration.convertToSeconds(service.model.data.snapshotInterval)
    recurring.log = True
    recurring.lastRun = 0

    recurring = service.model.dbobj.recurringActions[1]
    recurring.action = "cleanup"
    recurring.period = j.data.types.duration.convertToSeconds("1d")
    recurring.log = True
    recurring.lastRun = 0
    service.saveAll()


def snapshot(job):
    """Taking snapshot of all machines in the given space if it meets the conditions specified in the schema"""
    from dateutil import parser
    import datetime

    service = job.service
    START_DATE = parser.parse(service.model.data.startDate) if service.model.data.endDate != "" else ""
    END_DATE = parser.parse(service.model.data.endDate) if service.model.data.endDate != "" else ""

    start_date_valid = START_DATE == "" or START_DATE < datetime.datetime.now()
    end_date_valid = END_DATE == "" or END_DATE > datetime.datetime.now()

    if start_date_valid and end_date_valid:
        # Get spaces id from the parent (vdc)
        vdc = service.producers["vdc"][0]
        # Get given space resides in g8client
        g8client = vdc.producers["g8client"][0]
        cl = j.clients.openvcloud.getFromService(g8client)
        cl = cl.account_get(vdc.model.data.account)
        space = cl.space_get(vdc.name, vdc.model.data.location)
        for name, machine in space.machines.items():
            machine.create_snapshot()


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

    for name, machine in space.machines.items():
        for snapshot in machine.list_snapshots():
            # Get the delta time in seconds
            delta = int(time.time()) - snapshot['epoch']
            if delta > RETENTION:
                machine.delete_snapshot(snapshot['epoch'])
