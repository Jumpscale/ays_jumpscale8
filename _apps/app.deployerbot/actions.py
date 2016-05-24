from JumpScale import j


class Actions(ActionsBaseMgmt):

    def install(self, service):
        if 'webserver' not in service.producers:
            raise j.exceptions.NotFound("Can't find producer webserver")

        # confgiure reverse proxy to server flask app
        ws = service.producers['webserver'][0]
        address = service.hrd.getStr('oauth.host')
        port = service.hrd.getInt('oauth.port')
        ws.actions.add_proxy(ws, "/", address=address, port=port, trimPrefix=False)

        service.executor.cuisine.apps.deployerbot.build(
            start=True,
            token=service.hrd.getStr('token'),
            g8_addresses=service.hrd.getList('g8.addresses'),
            dns=service.hrd.getDictFromPrefix('dns'),
            oauth=service.hrd.getDictFromPrefix('oauth'))

    def start(self, service):
        cmd = service.executor.cuisine.core.args_replace('jspython telegram-bot --config $cfgDir/deployerbot/config.toml')
        cwd = service.executor.cuisine.core.args_replace("$appDir/deployerbot")
        service.executor.cuisine.processmanager.ensure('deployerbot', cmd=cmd, path=cwd)

    def stop(self, service):
        service.executor.cuisine.processmanager.stop('deployerbot')
