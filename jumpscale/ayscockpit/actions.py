def install(job):
    service = job.service
    cuisine = service.executor.cuisine

    if 'redis' not in service.producers:
        raise j.exceptions.AYSNotFound("Can't find redis service in producers.")

    # configure redis connection for AYS
    redis = service.producers['redis'][0]
    # this line create the default config if it doesn't exsits yet
    config = j.atyourservice.config

    if redis.model.data.unixsocket != '':
        config['redis']['unixsocket'] = redis.model.data.unixsocket
    else:
        config['redis'] = {
            'host': redis.model.data.host,
            'port': redis.model.data.port,
        }

    cfg_path = cuisine.core.args_replace('$cfgDir/ays/ays.conf')
    cuisine.core.dir_ensure(j.sal.fs.getParent(cfg_path))
    cuisine.core.file_write(cfg_path, j.data.serializer.toml.dumps(config))

    # configure AYS daemon
    cmd = 'ays start'
    pm = cuisine.processmanager.get('tmux')
    pm.ensure(cmd=cmd, name='cockpit_daemon_%s' % service.name, path=j.sal.fs.getParent(cfg_path))

    # configure REST API
    raml = cuisine.core.file_read('$appDir/ays_api/ays_api/apidocs/api.raml')
    raml = raml.replace('$(baseuri', "%s/api" % service.model.data.dnsDomain)
    cuisine.core.file_write('$appDir/ays_api/ays_api/apidocs/api.raml', raml)

    cmd = 'jspython api_server'
    pm.ensure(cmd=cmd, name='cockpit_api_%s' % service.name, path=cuisine.core.args_replace('$appDir/ays_api'))


def start(job):
    service = job.service
    cuisine = service.executor.cuisine

    pm = cuisine.processmanager.get('tmux')

    cmd = 'ays start'
    pm.ensure(cmd=cmd, name='cockpit_daemon_%s' % service.name, path=cuisine.core.args_replace('$cfgDir/ays'))

    cmd = 'jspython api_server'
    pm.ensure(cmd=cmd, name='cockpit_api_%s' % service.name, path=cuisine.core.args_replace('$appDir/ays_api'))


def stop(job):
    service = job.service
    cuisine = service.executor.cuisine
    pm = cuisine.processmanager.get('tmux')
    pm.stop(name='cockpit_api_%s' % service.name)
    pm.stop(name='cockpit_daemon_%s' % service.name)
