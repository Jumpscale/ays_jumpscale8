from JumpScale import j


class Actions(ActionsBaseMgmt):

    def install(self, service):
        if self.service.hrd.get('aysfs'):
            self.service.executor.cuisine.installer.jumpscale8()
        else:
            self.service.executor.cuisine.installerdevelop.jumpscale8()
