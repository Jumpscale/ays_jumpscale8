
class Actions():

    @action
    def install(self):
        self.monitor()

    @action
    def monitor(self):
        g=self.getGithubClient()
        #@todo implement test

    def getGithubClient(self):
        g=j.clients.github.getClient("$(github.secret)")
        return g

    @action
    def test(self):
        print ("test")

    @action
    def test2(self):
        print ("test2")        
        print ("$(github.secret)")        

    @action(queue="main")
    def testasync(self):
        print ("testasync")        
        print ("$(github.secret)")                