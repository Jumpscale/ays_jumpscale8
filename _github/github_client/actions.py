from JumpScale import j


class Actions():

    def init(self):
        return True

    def install(self):
        self.monitor()

    def monitor(self):
        g=self.getGithubClient()
        #@todo implement test

    def getGithubClient(self):
        g=j.clients.github.getClient("$(github.secret)")
        return g

    def action_test(self):
        print ("test")