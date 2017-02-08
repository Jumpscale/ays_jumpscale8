def install(job):
    """
    Installing appscale
    """
    service = job.service
    cuisine = service.executor.cuisine

    appscale_tag = service.model.data.appscaletag
    cuisine.apps.appscale.build(tag=appscale_tag)
