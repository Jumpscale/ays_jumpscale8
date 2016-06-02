from JumpScale import j


class Actions(ActionsBaseMgmt):

    def install(self, service):
        service.executor.cuisine.apps.cockpit.build(start=True, bot_token=service.hrd.get('telegram.token'),
                                                    jwt_key=service.hrd.get('jwt.key'), organization='')
