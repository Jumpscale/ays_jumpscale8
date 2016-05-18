from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self, service):
        return True

    def install(self, service):
        service.executor.cuisine.installer.jumpscale8()

    def start(self, service):
        service.executor.cuisine.core.run('js8 start')

    def stop(self, service):
        service.executor.cuisine.core.run('js8 stop')
