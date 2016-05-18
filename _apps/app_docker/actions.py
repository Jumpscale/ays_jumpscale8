from JumpScale import j


class Actions(ActionsBaseMgmt):
    def install(self, service):
        service.executor.cuisine.docker.install()

    def start(self, service):
        pass

    def stop(self, service):
        pass

    def monitor(self, service):
        pass
