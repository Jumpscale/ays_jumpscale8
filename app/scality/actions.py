def install(job):
    """
    Scality is already available in the sandbox, no need to install or copy files.
    Instead, we will reconfigure it to use the provided storage and meta paths.
    """
    service = job.service

    cuisine = service.executor.cuisine
    cuisine.core.dir_ensure(service.model.data.storageData)
    cuisine.core.dir_ensure(service.model.data.storageMeta)

    env = {
        'S3DATAPATH': service.model.data.storageData,
        'S3METADATAPATH': service.model.data.storageMeta,
    }

    cuisine.processmanager.ensure(
        name='scalityS3',
        cmd='npm start',
        env=env,
        path='/opt/jumpscale8/apps/S3'
    )
