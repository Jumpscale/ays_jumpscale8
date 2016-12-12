def install(job):
    service = job.service
    cuisine = service.executor.cuisine

    if 'redis' not in service.producers:
        raise j.exceptions.AYSNotFound("Can't find redis service in producers.")

    # configure redis connection for AYS
    redis = service.producers['redis'][0]
    # this line create the default config if it doesn't exsits yet
    cfg_path = cuisine.core.args_replace("$JSCFGDIR/jumpscale/ays.yaml")
    config = j.data.serializer.yaml.loads("redis:\n    host: 'localhost'\n    port: 6379\n")
    if cuisine.core.file_exists(cfg_path):
        config = j.data.serializer.yaml.loads(cuisine.core.file_read(cfg_path))
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

    # change codedir path in system.yaml to be /optvar/code
    dir_paths = {
        'CODEDIR': cuisine.core.args_replace('$VARDIR/code'),
        'JSBASE': cuisine.core.dir_paths['base'],
        'CFGDIR': cuisine.core.dir_paths['JSCFGDIR'],
        'DATADIR': cuisine.core.args_replace('$VARDIR/data/'),
        'TMPDIR': '/tmp',
        'VARDIR': cuisine.core.dir_paths['VARDIR']
        }

    branch = 'master'
    cfg_path = cuisine.core.args_replace("$optDir/build.yaml")
    if cuisine.core.file_exists(cfg_path):
        config = j.data.serializer.yaml.loads(cuisine.core.file_read(cfg_path))
        if 'jumpscale' in config:
            branch = config['jumpscale']

    config = {
        'dirs': dir_paths,
        'identity': {'EMAIL': '', 'FULLNAME': '', 'GITHUBUSER': ''},
        'system': {'AYSBRANCH': branch, 'DEBUG': False, 'JSBRANCH': branch, 'SANDBOX': True}
        }
    cfg_path = cuisine.core.args_replace("$JSCFGDIR/jumpscale/system.yaml")
    cuisine.core.dir_ensure('$VARDIR/code/')
    if cuisine.core.file_exists(cfg_path):
        config = j.data.serializer.yaml.loads(cuisine.core.file_read(cfg_path))

        if 'dirs' in config:
            config['dirs']['CODEDIR'] = cuisine.core.args_replace('$VARDIR/code/')

    else:
        dir_paths = {
            'CODEDIR': cuisine.core.args_replace('$VARDIR/code'),
            'JSBASE': cuisine.core.dir_paths['base'],
            'CFGDIR': cuisine.core.dir_paths['JSCFGDIR'],
            'DATADIR': cuisine.core.args_replace('$VARDIR/data/'),
            'TMPDIR': '/tmp',
            'VARDIR': cuisine.core.dir_paths['VARDIR']
            }

        build_path = cuisine.core.args_replace("$optDir/build.yaml")
        branch = 'master'
        if cuisine.core.file_exists(cfg_path):
            build_versions = j.data.serializer.yaml.loads(cuisine.core.file_read(build_path))
            if 'jumpscale' in build_versions:
                branch = build_versions['jumpscale']

        config = {
            'dirs': dir_paths,
            'identity': {'EMAIL': '', 'FULLNAME': '', 'GITHUBUSER': ''},
            'system': {'AYSBRANCH': branch, 'DEBUG': False, 'JSBRANCH': branch, 'SANDBOX': True}
            }

    cuisine.core.dir_ensure(j.sal.fs.getParent(cfg_path))
    cuisine.core.file_write(cfg_path, j.data.serializer.yaml.dumps(config))
    # write logginf.yaml if it does not exists
    logging_path = cuisine.core.args_replace("$JSCFGDIR/jumpscale/logging.yaml")
    if not cuisine.core.file_exists(logging_path):
        loggin_config = {'mode': 'DEV', 'level': 'DEBUG', 'filter': ['j.sal.fs', 'j.data.hrd', 'j.application']}
        cusine.core.file_write(loggin_path, j.data.serializer.yaml.dumps(loggin_config))

    # configure REST API
    raml = cuisine.core.file_read('$JSAPPDIR/ays_api/ays_api/apidocs/api.raml')
    raml = raml.replace('$(baseuri)', "https://%s/api" % service.model.data.domain)
    cuisine.core.file_write('$JSAPPDIR/ays_api/ays_api/apidocs/api.raml', raml)
    content = cuisine.core.file_read('$JSAPPDIR/portals/main/base/AYS81/.space/nav.wiki')
    if 'REST API:/api' not in content:
        cuisine.core.file_write('$JSAPPDIR/portals/main/base/AYS81/.space/nav.wiki',
                                'REST API:/api',
                                append=True)
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
    cuisine.core.file_write('$JSCFGDIR/cockpit_api/config.toml', j.data.serializer.toml.dumps(api_cfg))

    # installed required package
    cuisine.package.mdupdate()
    cuisine.package.install('git')

    # start daemon
    cmd = 'ays start'
    pm = cuisine.processmanager.get('tmux')
    pm.ensure(cmd=cmd, name='cockpit_daemon_%s' % service.name)

    # start api
    cmd = 'jspython api_server'
    pm.ensure(cmd=cmd, name='cockpit_api_%s' % service.name, path=cuisine.core.args_replace('$JSAPPDIR/ays_api'))
    # upload the aysrepo used in installing to the cockpit
    cuisine.core.dir_ensure('$VARDIR/cockpit_repos')
    cuisine.core.upload(service.aysrepo.path, '$VARDIR/cockpit_repos/cockpit')
    cuisine.core.run('cd $VARDIR/cockpit_repos/cockpit; ays restore', profile=True)


def start(job):
    service = job.service
    cuisine = service.executor.cuisine

    pm = cuisine.processmanager.get('tmux')

    cmd = 'ays start'
    pm.ensure(cmd=cmd, name='cockpit_daemon_%s' % service.name)

    # in case we update the sandbox, need to reconfigure the raml with correct url
    raml = cuisine.core.file_read('$JSAPPDIR/ays_api/ays_api/apidocs/api.raml')
    raml = raml.replace('$(baseuri)', "https://%s/api" % service.model.data.domain)
    cuisine.core.file_write('$JSAPPDIR/ays_api/ays_api/apidocs/api.raml', raml)
    cmd = 'jspython api_server'
    pm.ensure(cmd=cmd, name='cockpit_api_%s' % service.name, path=cuisine.core.args_replace('$JSAPPDIR/ays_api'))


def stop(job):
    service = job.service
    cuisine = service.executor.cuisine
    pm = cuisine.processmanager.get('tmux')
    pm.stop(name='cockpit_api_%s' % service.name)
    pm.stop(name='cockpit_daemon_%s' % service.name)
