
def init(job):
    service = job.service
    if 'g8client' not in service.producers:
        raise j.exceptions.AYSNotFound("no producer g8client found. cannot continue init of %s" % service)

    if service.model.data.location == "":
        raise j.exceptions.Input("location argument cannot be empty, cannot continue init of %s" % service)

    g8client = service.producers["g8client"][0]
    if service.model.data.account == "":
        service.model.data.account = g8client.model.data.account


def install(job):
    service = job.service
    if 'g8client' not in service.producers:
        raise j.exceptions.AYSNotFound("no producer g8client found. cannot continue init of %s" % service)
    g8client = service.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(service.model.data.account)
    # if space does not exist, it will create it
    space = acc.space_get(service.model.dbobj.name, service.model.data.location)
    owners = space.owners
    authorized_users = space.authorized_users
    users = (user.name for user in service.producers.get('uservdc', []))  # Users to be authorized_users
    # Authorize users
    for user in users:
        if user not in authorized_users:
            space.authorize_user(username=user)

    # Unauthorize users not in the schema
    for user in authorized_users:
        if user not in users and user not in owners:
            space.unauthorize_user(username=user)


def processChange(job):
    service = job.service

    args = job.model.args

    if args["changeCategory"] == "dataschema":
        for key, value in args.items():
            if key != "changeCategory":
                setattr(service.model.data, key, value)

        if 'g8client' not in service.producers:
            raise j.exceptions.AYSNotFound("no producer g8client found. cannot continue init of %s" % service)

        g8client = service.producers["g8client"][0]
        cl = j.clients.openvcloud.getFromService(g8client)
        acc = cl.account_get(service.model.data.account)
        # Get given space, raise error if not found
        space = acc.space_get(name=service.model.dbobj.name,
                            location=service.model.data.location,
                            create=False)

        authorized_users = space.authorized_users
        users = service.model.data.vdcUsers  # Users to be authorized_users

        # Authorize users
        for user in users:
            if user not in authorized_users:
                space.authorize_user(username=user)

        # Unauthorize users not in the schema
        for user in authorized_users:
            if user not in users:
                space.unauthorize_user(username=user)

        service.save()


def uninstall(job):
    service = job.service
    if 'g8client' not in service.producers:
        raise j.exceptions.AYSNotFound("no producer g8client found. cannot continue init of %s" % service)

    g8client = service.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(service.model.data.account)
    space = acc.space_get(service.model.dbobj.name, service.model.data.location)
    space.delete()
