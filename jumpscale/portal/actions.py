
def install(job):
    service = job.service
    cuisine = service.executor.cuisine

    cfg = cuisine.core.file_read('$appDir/portals/main/config.hrd')
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
        cfg.set('param.cfg.redirect_url', service.model.data.oauthRedirectUrl)
        cfg.set('param.cfg.token_url', service.model.data.oauthTokenUrl)


    cuisine.core.file_write('$appDir/portals/main/config.hrd', str(cfg))

    cuisine.core.dir_ensure('$cfgDir/portals')
    cuisine.core.file_link('$appDir/portals/jslib', '$cfgDir/portals/jslib')
    if not cuisine.core.file_exists('$appDir/portals/main/base/AYS81'):
        cuisine.core.file_link('$codeDir/github/jumpscale/jumpscale_portal8/apps/portalbase/AYS81', '$appDir/portals/main/base/AYS81')

    cmd = cuisine.core.args_replace('jspython portal_start.py')
    wd = cuisine.core.args_replace('$appDir/portals/main')
    pm = cuisine.processmanager.get('tmux')
    pm.ensure('portal_%s' % service.name, cmd=cmd, path=wd)


def start(job):
    service = job.service
    cuisine = service.executor.cuisine
    cmd = cuisine.core.args_replace('jspython portal_start.py')
    wd = cuisine.core.args_replace('$appDir/portals/main')
    pm = cuisine.processmanager.get('tmux')
    pm.ensure('portal_%s' % service.name, cmd=cmd, path=wd)


def stop(job):
    service = job.service
    cuisine = service.executor.cuisine
    pm = cuisine.processmanager.get('tmux')
    pm.stop('portal_%s' % service.name)


