def install(job):
    service = job.service
    cuisine = job.service.executor.cuisine
    base_bot_path = "$codeDir/github/jumpscale/jscockpit/ays_bot"
    if not cuisine.core.dir_exists(base_bot_path):
        cuisine.development.git.pullRepo('https://github.com/Jumpscale/jscockpit', ssh=False)

    cuisine.core.file_copy(base_bot_path, "$appDir", recursive=True)
    cfg = {'token': service.model.data.botToken,
           'oauth': {
               'host': service.model.data.oauthHost,
               'port': service.model.data.oauthPort,
               'organization': service.model.data.oauthClient,
               'client_id': service.model.data.oauthClient,
               'client_secret': service.model.data.oauthSecret,
               'redirect_uri': service.model.data.oauthRedirect,
               'itsyouonlinehost': service.model.data.oauthItsyouonlinehost
               }
           }
    config = j.data.serializer.toml.dumps(cfg)

    cuisine.core.dir_ensure("$cfgDir/ays_bot")
    cuisine.core.file_write("$cfgDir/ays_bot/config.toml", config)

    cuisine.processmanager.ensure(name="ays_bot",
                                  cmd="jspython ays-bot -c $cfgDir/ays_bot/config.toml",
                                  path="$appDir/ays_bot")
