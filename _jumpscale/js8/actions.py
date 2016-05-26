from JumpScale import j


class Actions(ActionsBaseMgmt):

    def install(self, service):
        if service.hrd.getBool('aysfs'):
            service.executor.cuisine.installer.jumpscale8()
        else:
            service.executor.cuisine.installerdevelop.jumpscale8()
