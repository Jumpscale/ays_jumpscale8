def install(job):
    """
    Installing owncloud
    """
    service = job.service
    cuisine = service.executor.cuisine

    cuisine.apps.owncloud.install(start=False)

    tidb = service.producers['tidb'][0]
    tidbos = tidb.parent
    tidbdocker = tidbos.parent
    tidbhost = tidbdocker.model.data.ipPrivate

    tidbuser = service.model.data.tidbuser
    tidbpassword = service.model.data.tidbpassword
    # dbhost=tidb.model.data.dbhost
    # dbuser=tidb.model.data.dbuser
    # dbpass=tidb.model.data.dbpass

    #cuisine.apps.owncloud.install(start=False)
    cuisine.apps.owncloud.start(sitename=sitename, dbhost=tidbhost, dbuser=tidbuser, dbpass=tidbpassword)
