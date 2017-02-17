def install(job):
    """
    Installing appscale
    """
    service = job.service
    cuisine = service.executor.cuisine
    data = service.model.data
    client_id = data.clientId
    client_secret = data.clientSecret
    build_path = cuisine.apps.oca.build(client_id=client_id, client_secret=client_secret)
    cuisine.core.run("cd /root && appscale deploy %s" % build_path, die=True)
