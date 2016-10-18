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

    # configure AYS daemon
    cmd = 'ays start --conf %s' % cfg_path
    pm = cuisine.processmanager.get('tmux')
    pm.ensure(cmd=cmd, name='cockpit_daemon_%s' % service.name, path=j.sal.fs.getParent(cfg_path))

    # configure REST API
    raml = cuisine.core.file_read('$appDir/ays_api/ays_api/apidocs/api.raml')
    raml = raml.replace('$(baseuri', "%s/api" % service.model.data.dnsDomain)
    cuisine.core.file_write('$appDir/ays_api/ays_api/apidocs/api.raml', raml)

    cmd = 'jspython api_server'
    pm.ensure(cmd=cmd, name='cockpit_api_%s' % service.name, path='$appDir/ays_api')


def start(job):
    service = job.service
    cuisine = service.executor.cuisine

    pm = cuisine.processmanager.get('tmux')
    pm.start(name='cockpit_%s' % service.name)


def stop(job):
    service = job.service
    cuisine = service.executor.cuisine
    pm = cuisine.processmanager.get('tmux')
    pm.stop(name='cockpit_%s' % service.name)
