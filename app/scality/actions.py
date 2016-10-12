def install(job):
    """
    Scality is already available in the sandbox, no need to install or copy files.
    Instead, we will reconfigure it to use the provided storage and meta paths.
    """
    service = job.service

    cuisine = service.executor.cuisine
    cuisine.core.dir_ensure(service.data.model.storageData)
    cuisine.core.dir_ensure(service.data.model.storageMeta)

    env = {
        'S3DATAPATH': service.data.model.storageData,
        'S3METADATAPATH': service.data.model.storageMeta,
    }

    cuisine.processmanager.ensure(
        name='scalityS3',
        cmd='npm start',
        env=env,
        path='/opt/jumpscale8/apps/S3'
    )
