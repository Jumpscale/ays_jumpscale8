def install(job):
    cuisine = job.service.executor.cuisine

    bin_location = cuisine.core.command_location('fs')
    if bin_location is None or bin_location == '':
        # If we don't have fs pre-install, download it and install it
        cuisine.core.dir_ensure('/usr/local/bin')
        cuisine.core.file_download('https://stor.jumpscale.org/public/fs', '/usr/local/bin/fs')
        cuisine.core.file_attribs('/usr/local/bin/fs', '0550')

    service = job.service
    cuisine = service.executor.cuisine

    final_config = {
        'mount': [],
        'backend': {},
        'aydostor': {},
    }

    for config in service.producers['vfs_config']:
        # TODO download flist
        flist_path = cuisine.core.args_replace('$tmpDir/%s' % j.sal.fs.getBaseName(config.model.data.mountFlist))
        cuisine.core.file_download(config.model.data.mountFlist, flist_path)

        mount = {
            'path': config.model.data.mountMountpoint,
            'flist': flist_path,
            'backend': config.name,
            'mode': config.model.data.mountMode,
            'trim_base': config.model.data.mountTrimbase,
        }

        cuisine.core.dir_ensure(config.model.data.backendPath)
        backend = {
            'path': config.model.data.backendPath,
            'stor': config.name,
            'namespace': config.model.data.backendNamespace,
            'upload': config.model.data.backendUpload,
            'encrypted': config.model.data.backendEncrypted,
            'user_rsa': config.model.data.backendUserRsa,
            'store_rsa': config.model.data.backendStoreRsa,
            'aydostor_push_cron': config.model.data.backendPush,
            'cleanup_cron': config.model.data.backendCleanupCron,
            'cleanup_older_than': config.model.data.backendCleanupOld,
        }

        store = {
            'addr': config.model.data.storeUrl,
            'login': config.model.data.storeLogin,
            'passwd': config.model.data.storePassword,
        }

        final_config['mount'].append(mount)
        final_config['backend'][config.name] = backend
        final_config['aydostor'][config.name] = store

    # make sure nonthing is already mounted
    for mount in final_config['mount']:
        cmd = 'umount -fl %s' % mount['path']
        cuisine.core.run(cmd, die=False)

    # create all mountpoints but make sure we don't create folder inside mountpoints in the cases
    # we would have a mountpoint inside another
    # e.g for two mountpoints:
    # /mnt/root
    # /mnt/root/opt
    # we only create /mnt/root
    tocreate = {m['path'] for m in final_config['mount']}
    todelete = set()
    for path in tocreate:
        if j.sal.fs.getParent(path) in tocreate:
            todelete.add(path)

    for path in tocreate.difference(todelete):
        cuisine.core.dir_ensure(path)

    # write config
    config_path = cuisine.core.args_replace('$cfgDir/fs/%s.toml' % service.name)
    cuisine.core.file_write(config_path, j.data.serializer.toml.dumps(final_config))

    # create service
    pm = cuisine.processmanager.get('tmux')
    bin_location = cuisine.core.command_location('fs')
    cmd = '%s -config %s' % (bin_location, config_path)
    pm.ensure("fs_%s" % service.name, cmd=cmd, env={}, path='$cfgDir/fs', descr='G8OS FS')


def stop(job):
    pass
