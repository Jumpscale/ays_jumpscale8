def input(job):
    args = job.model.args

    # Validating startDate argument
    if "startDate" not in args:
        args["startDate"] = ""

    # Validating endDate argument
    if "endDate" not in args:
        args["endDate"] = ""

    # Add default value to snapshotInterval argument if empty or None
    if "snapshotInterval" not in args or args["snapshotInterval"].strip() == "":
        args["snapshotInterval"] = "2h"

    # Add default value to retention argument if empty or None
    if "retention" not in args or args["retention"].strip() == "":
        args["retention"] = "5d"

    return args


def install(job):
    service = job.service

    """Configure recurring actions"""
    RECURRING_ACTION_COUNT = 2
    service.model.dbobj.init("recurringActions", RECURRING_ACTION_COUNT)

    recurring = service.model.dbobj.recurringActions[0]
    recurring.action = "snapshot"
    recurring.period = j.data.types.duration.convertToSeconds(service.model.data.snapshotInterval)
    recurring.log = True
    recurring.lastRun = 0

    recurring = service.model.dbobj.recurringActions[1]
    recurring.action = "cleanup"
    recurring.period = j.data.types.duration.convertToSeconds("30s")
    recurring.log = True
    recurring.lastRun = 0
    service.saveAll()


def snapshot(job):
    from dateutil import parser
    import datetime

    def create_snapshot(service):
        # Get spaces id from the parent (vdc)
        vdc = service.producers["vdc"][0]
        # Get given space resides in g8client
        g8client = vdc.producers["g8client"][0]
        cl = j.clients.openvcloud.getFromService(g8client)
        cl = cl.account_get(vdc.model.data.account)
        space = cl.space_get(vdc.name, vdc.model.data.location)
        for name, machine in space.machines.items():
            machine.create_snapshot()

    def date_input(date):
        if date != "":
            parser.parse(service.model.data.startDate)
        return date

    service = job.service
    START_DATE = date_input(service.model.data.startDate)
    END_DATE = date_input(service.model.data.endDate)

    start_date_valid = START_DATE == "" or START_DATE < datetime.datetime.now()
    end_date_valid = END_DATE == "" or END_DATE > datetime.datetime.now()
    if start_date_valid and end_date_valid:
            create_snapshot(service)


def cleanup(job):
    from dateutil import parser
    import datetime
    import re

    service = job.service
    RETENTION = int(re.findall('\d+', service.model.data.retention)[0])

    # Get spaces id from the parent (vdc)
    vdc = service.producers["vdc"][0]
    # Get given space resides in g8client
    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    cl = cl.account_get(vdc.model.data.account)
    space = cl.space_get(vdc.name, vdc.model.data.location)

    for name, machine in space.machines.items():
        for snapshot in machine.list_snapshots():
            delta = datetime.datetime.now() - parser.parse(snapshot)
            if delta > RETENTION:
                machine.deleteSnapshot(snapshot['name'], snapshot['epoch'])

