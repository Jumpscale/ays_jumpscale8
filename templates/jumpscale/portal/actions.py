
def install(job):
    service = job.service
    cuisine = service.executor.cuisine

    cfg = cuisine.core.file_read('$tmplsDir/cfg/portal/config.hrd')
    cfg = j.data.hrd.get(content=cfg, prefixWithName=False)

    # configure portal basics
    cfg.set('param.cfg.ipaddr', service.model.data.listenAddr)
    cfg.set('param.cfg.port', service.model.data.listenPort)
    cfg.set('param.cfg.defaultspace', service.model.data.spaceDefault)


    # configure portal for oauth
    if service.model.data.oauthEnabled:
        data_json = j.data.serializer.json.loads(service.model.dataJSON)
        keys = [j.data.hrd.sanitize_key(k) for k in data_json.keys() if k.startswith('oauth')]
        for key in keys:
            missing = []
            if data_json[key] is None or data_json[key] == '':
                missing.append(key)
        if len(missing) > 0:
            if len(missing) == 1:
                raise j.exceptions.Input("Argument is missing to enable oauth. (%s)" % missing[0])
            else:
                raise j.exceptions.Input("Arguments are missing to enable oauth. (%s)" % ','.join(missing))

        cfg.set('param.cfg.client_id', service.model.data.oauthClientId)
        cfg.set('param.cfg.client_scope', service.model.data.oauthScope)
        cfg.set('param.cfg.client_secret', service.model.data.oauthSecret)
        cfg.set('param.cfg.client_url', service.model.data.oauthClientUrl)
        cfg.set('param.cfg.client_user_info_url', service.model.data.oauthClientUserInfoUrl)
        cfg.set('param.cfg.force_oauth_instance', service.model.data.oauthProvider)
        cfg.set('param.cfg.oauth.default_groups', [i for i in service.model.data.oauthDefaultGroups])
        cfg.set('param.cfg.organization', service.model.data.oauthOrganization)

        if service.model.data.oauthRedirectUrl.split('/')[2] == '':  # if no domain is set use ip instead
            node = service.aysrepo.servicesFind(actor='node.*')[0]
            redirect_url = service.model.data.oauthRedirectUrl.split('/')
            redirect_url[2] = node.model.data.ipPublic
            #  if not domain use http instead of https
            redirect_url[0] = 'http:'
            service.model.data.oauthRedirectUrl = '/'.join(redirect_url)

        cfg.set('param.cfg.redirect_url', service.model.data.oauthRedirectUrl)
        cfg.set('param.cfg.token_url', service.model.data.oauthTokenUrl)


    cuisine.core.file_write('$cfgDir/portals/main/config.hrd', str(cfg))

    cuisine.core.dir_ensure('$cfgDir/portals')
    if not cuisine.core.file_exists('$appDir/portals/main/base/AYS81'):
        cuisine.core.file_link('$codeDir/github/jumpscale/jumpscale_portal8/apps/portalbase/AYS81', '$appDir/portals/main/base/AYS81')
    # make sure system.yaml exists at this step
    # change codedir path in system.yaml to be /optvar/code
    dir_paths = {
        'CODEDIR': cuisine.core.args_replace('$varDir/code'),
        'JSBASE': cuisine.core.dir_paths['base'],
        'CFGDIR': cuisine.core.dir_paths['cfgDir'],
        'DATADIR': cuisine.core.args_replace('$varDir/data/'),
        'TMPDIR': '/tmp',
        'VARDIR': cuisine.core.dir_paths['varDir']
        }

    branch = 'master'
    build_path = cuisine.core.args_replace("$optDir/build.yaml")
    if cuisine.core.file_exists(build_path):
        versions = j.data.serializer.yaml.loads(cuisine.core.file_read(build_path))
        if 'jumpscale' in versions:
            branch = versions['jumpscale']

    config = {
        'dirs': dir_paths,
        'identity': {'EMAIL': '', 'FULLNAME': '', 'GITHUBUSER': ''},
        'system': {'AYSBRANCH': branch, 'DEBUG': False, 'JSBRANCH': branch, 'SANDBOX': True}
        }
    cfg_path = cuisine.core.args_replace("$cfgDir/jumpscale/system.yaml")
    cuisine.core.dir_ensure('$varDir/code/')
    if cuisine.core.file_exists(cfg_path):
        config = j.data.serializer.yaml.loads(cuisine.core.file_read(cfg_path))
        if 'dirs' in config:
            config['dirs']['CODEDIR'] = cuisine.core.args_replace('$varDir/code/')
    cuisine.core.dir_ensure(j.sal.fs.getParent(cfg_path))
    cuisine.core.file_write(cfg_path, j.data.serializer.yaml.dumps(config))
    # make sure logging.yaml exists
    logging_path = cuisine.core.args_replace("$cfgDir/jumpscale/logging.yaml")
    if not cuisine.core.file_exists(logging_path):
        logging_config = {'mode': 'DEV', 'level': 'DEBUG', 'filter': ['j.sal.fs', 'j.data.hrd', 'j.application']}
        cuisine.core.file_write(logging_path, j.data.serializer.yaml.dumps(logging_config))
    cmd = cuisine.core.args_replace('jspython portal_start.py')
    wd = cuisine.core.args_replace('$appDir/portals/main')
    pm = cuisine.processmanager.get('tmux')
    pm.ensure('portal_%s' % service.name, cmd=cmd, path=wd, autostart=True)


def start(job):
    service = job.service
    cuisine = service.executor.cuisine
    cmd = cuisine.core.args_replace('jspython portal_start.py')
    wd = cuisine.core.args_replace('$appDir/portals/main')
    pm = cuisine.processmanager.get('tmux')
    pm.ensure('portal_%s' % service.name, cmd=cmd, path=wd, autostart=True)


def stop(job):
    service = job.service
    cuisine = service.executor.cuisine
    pm = cuisine.processmanager.get('tmux')
    pm.stop('portal_%s' % service.name)
