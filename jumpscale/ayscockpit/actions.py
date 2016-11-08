def install(job):
    service = job.service
    cuisine = service.executor.cuisine

    if 'redis' not in service.producers:
        raise j.exceptions.AYSNotFound("Can't find redis service in producers.")

    # configure redis connection for AYS
    redis = service.producers['redis'][0]
    # this line create the default config if it doesn't exsits yet
    cfg_path = cuisine.core.args_replace("$cfgDir/jumpscale/ays.yaml")
    config = cuisine.core.file_read(cfg_path)
    if 'redis' not in config:
        config['redis'] = {}

    # configure AYS daemon
    if redis.model.data.unixsocket != '':
        config['redis']['unixsocket'] = redis.model.data.unixsocket
    else:
        config['redis'] = {
            'host': redis.model.data.host,
            'port': redis.model.data.port,
        }

    cuisine.core.dir_ensure(j.sal.fs.getParent(cfg_path))
    cuisine.core.file_write(cfg_path, j.data.serializer.yaml.dumps(config))

    # configure REST API
    raml = cuisine.core.file_read('$appDir/ays_api/ays_api/apidocs/api.raml')
    raml = raml.replace('$(baseuri)', "https://%s/api" % service.model.data.domain)
    cuisine.core.file_write('$appDir/ays_api/ays_api/apidocs/api.raml', raml)
    api_cfg = {
        'oauth':{
            'client_secret': service.model.data.oauthClientSecret,
            'client_id': service.model.data.oauthClientId,
            'organization': service.model.data.oauthOrganization,
            'jwt_key': service.model.data.oauthJwtKey,
            'redirect_uri': service.model.data.oauthRedirectUrl,
        },
        'api':{
            'ays':{
                'host': service.model.data.apiHost,
                'port': service.model.data.apiPort,
            }
        }
    }
    cuisine.core.file_write('$cfgDir/cockpit_api/config.toml', j.data.serializer.toml.dumps(api_cfg))

    # installed required package
    cuisine.package.mdupdate()
    cuisine.package.install('git')

    # start daemon
    cmd = 'ays start'
    pm = cuisine.processmanager.get('tmux')
    pm.ensure(cmd=cmd, name='cockpit_daemon_%s' % service.name, path=j.sal.fs.getParent(cfg_path))

    # start api
    cmd = 'jspython api_server'
    pm.ensure(cmd=cmd, name='cockpit_api_%s' % service.name, path=cuisine.core.args_replace('$appDir/ays_api'))


def start(job):
    service = job.service
    cuisine = service.executor.cuisine

    pm = cuisine.processmanager.get('tmux')

    cmd = 'ays start'
    pm.ensure(cmd=cmd, name='cockpit_daemon_%s' % service.name, path=cuisine.core.args_replace('$cfgDir/ays'))

    # in case we update the sandbox, need to reconfigure the raml with correct url
    raml = cuisine.core.file_read('$appDir/ays_api/ays_api/apidocs/api.raml')
    raml = raml.replace('$(baseuri)', "https://%s/api" % service.model.data.domain)
    cuisine.core.file_write('$appDir/ays_api/ays_api/apidocs/api.raml', raml)
    cmd = 'jspython api_server'
    pm.ensure(cmd=cmd, name='cockpit_api_%s' % service.name, path=cuisine.core.args_replace('$appDir/ays_api'))


def stop(job):
    service = job.service
    cuisine = service.executor.cuisine
    pm = cuisine.processmanager.get('tmux')
    pm.stop(name='cockpit_api_%s' % service.name)
    pm.stop(name='cockpit_daemon_%s' % service.name)
