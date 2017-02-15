def install(job):
    """
    Installing appscale
    """
    service = job.service

    appscale_tag = service.model.data.appscaletag
    for node in service.model.data.os:
        os = service.aysrepo.servicesFind(actor='os.*', name=node)[0]
        os.executor.cuisine.apps.appscale.build(tag=appscale_tag)
