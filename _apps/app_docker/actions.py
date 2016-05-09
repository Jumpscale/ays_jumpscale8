from JumpScale import j


class Actions(ActionsBaseMgmt):
    def install(self):
        self.service.executor.cuisine.docker.install()

    def start(self):
        pass

    def stop(self):
        pass

    def monitor(self):
        pass
