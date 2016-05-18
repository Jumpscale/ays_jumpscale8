from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self, service):
        return True

    def install(self, service):
        service.executor.cuisine.installer.jumpscale8()
