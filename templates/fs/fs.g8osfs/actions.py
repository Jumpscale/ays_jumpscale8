def install(job):
    cuisine = job.service.executor.cuisine

    cuisine.package.mdupdate()
    cuisine.package.install('fuse')
    cuisine.core.dir_ensure('/bin')
    cuisine.core.file_download('https://stor.jumpscale.org/public/g8ufs', '/bin/g8ufs')
    cuisine.core.file_download('https://stor.jumpscale.org/public/lib-dep.tar.gz', '$TMPDIR/lib-dep.tar.gz')
    cuisine.core.file_attribs('/bin/g8ufs', '0755')
    cuisine.core.run('tar -zxf $TMPDIR/lib-dep.tar.gz -C /usr/lib --strip-components 1')

    service = job.service
    cuisine = service.executor.cuisine

    flist_path = cuisine.core.replace('$TMPDIR/%s' % j.sal.fs.getBaseName(service.model.data.flist))
    cuisine.core.file_download(service.model.data.flist, flist_path, overwrite=True)
    meta_path = '$TMPDIR/meta'
    cuisine.core.dir_ensure(meta_path)
    cuisine.core.run('tar -zxf %s -C %s' % (flist_path, meta_path))
    cmd = 'umount -fl %s' % service.model.data.mountPoint
    cuisine.core.run(cmd, die=False)
    pm = cuisine.processmanager.get('tmux')
    cmd = 'g8ufs -meta %s -storage-url %s %s' % (meta_path, service.model.data.storageUrl, service.model.data.mountPoint)
    pm.ensure("fs_%s" % service.name, cmd=cmd, env={}, descr='G8OS FS', autostart=True, wait="3m")

    # wait until all targets are actually mounted
    # We wait max 1 min per target
    # NOTE: in real life, once one target is ready all targets would be there
    import time
    trials = 12
    while trials > 0:
        code, _, _ = cuisine.core.run('mount | grep -P "on {}\s"'.format(service.model.data.mountPoint), die=False)
        if code != 0:
            # not found yet. We sleep for 5 seconds
            time.sleep(5)
        else:
            break
        trials -= 1

def start(job):
    # the start needs all the steps from install so just re-call install
    service = job.service
    job = service.getJob('install')
    job.executeInProcess()

def stop(job):
    service = job.service
    cuisine = service.executor.cuisine

    pm = cuisine.processmanager.get('tmux')
    pm.stop('fs_%s' % service.name)
