from JumpScale import j


class Actions(ActionsBaseMgmt):

    def init(self):
        return True

    def install(self):
        self.monitor()

    def monitor(self):
        g=self.getGithubClient()
        #@todo implement test

    def getGithubClient(self):
        g=j.clients.github.getClient(self.service.hrd.get("github.secret"))
        return g
