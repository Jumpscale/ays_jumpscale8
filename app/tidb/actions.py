def install(job):
    """
    Installing owncloud
    """
    service = job.service
    cuisine = service.executor.cuisine

    clusterId = service.model.data.clusterId
    # dbname = service.model.data.dbname
    # dbuser = service.model.data.dbuser
    # dbpassword = service.model.data.dbpass

    cuisine.apps.tidb.start_pd_server()
    cuisine.apps.tidb.start_tikv()
    import time;
    time.sleep(5)
    cuisine.apps.tidb.start_tidb()
    cuisine.package.ensure('mysql-client')

    # import time
    # time.sleep(5)
    #
    # with cuisine.apps.tidb.dbman() as m:
    #     try:
    #         m.create_database(database=dbname)
    #         m.create_dbuser(host="127.0.0.1", username=dbuser, passwd=dbpassword)
    #     except:
    #         pass  # user created already.
    #     m.grant_user(host="127.0.0.1", username=dbuser, database=dbname)
