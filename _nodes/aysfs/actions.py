from JumpScale import j


class Actions():

    def init(self):
        return True

    def install(self):
        self.service.executor.cuisine.installer.jumpscale8()

    def start(self):
        self.service.executor.cuisine.core.run('js8 start')

    def stop(self):
        self.service.executor.cuisine.core.run('js8 stop')
