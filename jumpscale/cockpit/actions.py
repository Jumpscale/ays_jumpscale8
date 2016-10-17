def install(job):
    service = job.service
    cuisine = service.executor.cuisine

    if 'redis' not in service.producers:
        raise j.exceptions.AYSNotFound("Can't find redis service in producers.")

    redis = service.producers['redis'][0]
    daemon_cfg = {
        'redis': {}
    }
    if redis.model.data.unixsocket != '':
        daemon_cfg['redis']['unixsocket'] = redis.model.data.unixsocket
    else:
        daemon_cfg['redis'] = {
            'host': redis.model.data.host,
            'port': redis.model.data.port,
        }

    cfg_path = cuisine.core.args_replace('$cfgDir/ays/ays.conf')
    cuisine.core.dir_ensure(j.sal.fs.getParent(cfg_path))
    cuisine.core.file_write(cfg_path, j.data.serializer.toml.dumps(daemon_cfg))

    tmpl = """
    from JumpScale.baselib.atyourservice81.AtYourServiceDaemon import Server
    server = Server('{cfg_path}')
    server.start()
    """.format(cfg_path=cfg_path)
    cuisine.core.file_write('$binDir/ays_daemon', tmpl)

    cmd = 'jspython $binDir/ays_daemon'
    cuisine.processmanager.ensure(cmd=cmd, name='cockpit_%s' % service.name, path=j.sal.fs.getParent(cfg_path))


def start(job):
    service = job.service
    cuisine = service.executor.cuisine
    cuisine.processmanager.ensure(name='cockpit_%s' % service.name)


def stop(job):
    service = job.service
    cuisine = service.executor.cuisine
    cuisine.processmanager.ensure(name='cockpit_%s' % service.name)
