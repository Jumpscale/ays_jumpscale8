from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self):
        return True

    def install(self):
        service.executor.cuisine.installer.jumpscale8()
