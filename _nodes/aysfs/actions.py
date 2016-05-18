from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self):
        return True

    def install(self):
        service.executor.cuisine.installer.jumpscale8()

    def start(self):
        service.executor.cuisine.core.run('js8 start')

    def stop(self):
        service.executor.cuisine.core.run('js8 stop')
