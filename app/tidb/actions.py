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

    cuisine.apps.tidb.start()
    C = "apt-get update && apt-get install mysql-client-core-5.7 -y"
    cuisine.core.execute_bash(C)
