def install(job):
    """
    Installing owncloud
    """
    service = job.service
    cuisine = service.executor.cuisine

    cuisine.apps.owncloud.install(start=False)


def start(job):
    service = job.service
    cuisine = service.executor.cuisine
    cuisine.apps.owncloud.start(service.data.model.sitename)
