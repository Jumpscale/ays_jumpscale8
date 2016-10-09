def install(job):
    """Authorize user to given space"""
    service = job.service

    # Get space id from the parent (vdc)
    vdc = service.producers['vdc'][0]

    # Get userid, accesstype from args
    userid = service.model.data.userid

    # Get space from g8client
    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    cl = cl.account_get(vdc.model.data.account)
    space = cl.space_get(name=vdc.name, location=vdc.model.data.location)

    # Authorize user to given space
    space.authorize_user(username=userid)
