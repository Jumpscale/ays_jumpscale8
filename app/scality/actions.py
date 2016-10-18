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

    app_path = '/opt/jumpscale8/apps/S3'
    config_path = j.sal.fs.joinPaths(app_path, 'config.json')
    config_str = cuisine.core.file_read(config_path)
    config = j.data.serializer.json.loads(config_str)
    config['regions'] = {
        'us-east-1': [service.model.data.domain]
    }

    cuisine.core.file_write(
        config_path,
        j.data.serializer.json.dumps(config, indent=2)
    )

    pm = cuisine.processmanager.get('tmux')
    pm.ensure(
        name='scalityS3',
        cmd='npm start',
        env=env,
        path=app_path
    )
