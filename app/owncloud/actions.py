def install(job):
    """
    Installing owncloud
    """
    service = job.service
    cuisine = service.executor.cuisine

    sitename = service.model.data.sitename
    owncloudAdminUser = service.model.data.owncloudAdminUser
    owncloudAdminPassword = service.model.data.owncloudAdminPassword
    tidb = service.producers['tidb'][0]
    # dbhost=tidb.model.data.dbhost
    # dbuser=tidb.model.data.dbuser
    # dbpass=tidb.model.data.dbpass

    cuisine.apps.owncloud.install(start=False)
    cuisine.apps.owncloud.start(sitename=sitename)
