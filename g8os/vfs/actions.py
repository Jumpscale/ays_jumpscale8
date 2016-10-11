def install(job):
    cuisine = job.service.executor.cuisine

    bin_location = cuisine.core.command_location('fs')
    if bin_location is None or bin_location == '':
        # If we don't have fs pre-install, download it and install it
        cuisine.core.dir_ensure('/usr/local/bin')
        cuisine.core.file_download('https://stor.jumpscale.org/public/fs', '/usr/local/bin/fs')
        cuisine.core.file_attribs('/usr/local/bin/fs', '0550')


def start(job):
    cuisine = job.service.executor.cuisine
    service = job.service
    actor = service.aysrepo.actorGet(name=service.model.dbobj.actorName)

    cuisine.core.dir_ensure('$cfgDir/fs/flists')
    for flist in actor.model.dbobj.flists:
        args = {}
        args['flist_path'] = cuisine.core.args_replace('$cfgDir/fs/flists/%s' % flist.name)
        cuisine.core.file_write(args['flist_path'], flist.content)
        args['mountpoint'] = flist.mountpoint
        args['mode'] = flist.mode.__str__().upper()
        args['namespace'] = flist.namespace
        args['store_url'] = flist.storeUrl

        # make sure nonthing is already mounted there
        cmd = 'umount -fl %s' % args['mountpoint']
        cuisine.core.run(cmd, die=False)

        cuisine.core.dir_ensure(args['mountpoint'])

        config = """
        [[mount]]
            path="{mountpoint}"
            flist="{flist_path}"
            backend="main"
            mode = "{mode}"
            trim_base = true

        [backend.main]
            path="/storage/fs_backend"
            stor="stor1"
            namespace="{namespace}"

            upload=false
            encrypted=false
            # encrypted=true
            # user_rsa="user.rsa"
            # store_rsa="store.rsa"

            aydostor_push_cron="@every 1m"
            cleanup_cron="@every 1m"
            cleanup_older_than=1 #in hours

        [aydostor.stor1]
            addr="{store_url}"
        """.format(**args)
        config_path = cuisine.core.args_replace('$cfgDir/fs/%s.toml' % flist.name)
        cuisine.core.file_write(config_path, config)

        pm = cuisine.processmanager.get('tmux')
        bin_location = cuisine.core.command_location('fs')
        cmd = '%s -config %s' % (bin_location, config_path)
        pm.ensure("fs_%s" % flist.name, cmd=cmd, env={}, path='$cfgDir/fs', descr='G8OS FS')


def stop(job):
    cuisine = job.service.executor.cuisine
    service = job.service
    actor = service.aysrepo.actorGet(name=service.model.dbobj.actorName)

    for flist in actor.model.dbobj.flists:
        config_path = cuisine.core.args_replace('$cfgDir/fs/%s.toml' % flist.name)
        flist_config = cuisine.core.file_read(config_path)
        flist_config = j.data.serializer.toml.loads(flist_config)

        pm = cuisine.processmanager.get('tmux')
        pm.stop('fs_%s' % flist.name)

        for mount in flist_config['mount']:
            cmd = 'umount -fl %s' % mount['path']
            cuisine.core.run(cmd)


def processChange(job):
    service = job.service
    category = job.model.args.get('changeCategory', None)

    if category == 'config':
        service.runAction('stop')
        service.runAction('start')


def start_flist(job):
    args = job.model.args
    cuisine = job.service.executor.cuisine

    cuisine.core.dir_ensure('$cfgDir/fs/flists')
    flist_content = j.sal.fs.fileGetContents(args['flist'])
    flist_name = j.sal.fs.getBaseName(args['flist'])
    args['flist_path'] = cuisine.core.args_replace('$cfgDir/fs/flists/%s' % flist_name)
    cuisine.core.file_write(args['flist_path'], flist_content)

    # make sure nonthing is already mounted there
    cmd = 'umount -fl %s' % args['mountpoint']
    cuisine.core.run(cmd, die=False)

    cuisine.core.dir_ensure(args['mount_path'])

    config = """
    [[mount]]
        path="{mount_path}"
        flist="{flist_path}"
        backend="main"
        mode = "{mode}"
        trim_base = true

    [backend.main]
        path="/storage/fs_backend"
        stor="stor1"
        namespace="{namespace}"

        upload=false
        encrypted=false
        # encrypted=true
        # user_rsa="user.rsa"
        # store_rsa="store.rsa"

        aydostor_push_cron="@every 1m"
        cleanup_cron="@every 1m"
        cleanup_older_than=1 #in hours

    [aydostor.stor1]
        addr="{store_addr}"
    """.format(**args)
    config_path = cuisine.core.args_replace('$cfgDir/fs/%s.toml' % flist_name)
    cuisine.core.file_write(config_path, config)

    pm = cuisine.processmanager.get('tmux')
    bin_location = cuisine.core.command_location('fs')
    cmd = '%s -config %s' % (bin_location, config_path)
    pm.ensure("fs_%s" % flist_name, cmd=cmd, env={}, path='$cfgDir/fs', descr='G8OS FS')


def stop_flist(job):
    cuisine = job.service.executor.cuisine
    args = job.model.args

    flist_name = j.sal.fs.getBaseName(args['flist'])
    config_path = cuisine.core.args_replace('$cfgDir/fs/%s.toml' % flist_name)
    flist_config = cuisine.core.file_read(config_path)
    flist_config = j.data.serializer.toml.loads(flist_config)

    pm = cuisine.processmanager.get('tmux')
    pm.stop('fs_%s' % flist_name)

    for mount in flist_config['mount']:
        cmd = 'umount -fl %s' % mount['path']
        cuisine.core.run(cmd)
