def install(job):
    """
    Installing appscale tools
    """
    service = job.service
    cuisine = service.executor.cuisine

    appscale_tools_tag = service.model.data.appscaletag
    cuisine.apps.appscale.build_tools(appscale_tools_tag)
