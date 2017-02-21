def install(job):
    """
    Installing mobidick
    """
    service = job.service
    cuisine = service.executor.cuisine
    build_path = cuisine.apps.rogerthatmfr.build()
    cuisine.core.run("cd /root && appscale deploy %s" % build_path, die=True)
