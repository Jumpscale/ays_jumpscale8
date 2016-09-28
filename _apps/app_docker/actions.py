from JumpScale import j


class Actions(ActionsBaseMgmt):
    def getExecutor(self, service):
        os = service.producers['os'][0]
        return os.executor

    def install(self, service):
        service.executor.cuisine.systemservices.docker.install()

    def start(self, service):
        pass

    def stop(self, service):
        pass

    def monitor(self, service):
        pass
