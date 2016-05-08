
class Actions(ActionsBaseMgmt):

    def install(self):
        self.monitor()

    def monitor(self):
        g=self.getGithubClient()
        #@todo implement test

    def getGithubClient(self):
        g=j.clients.github.getClient(self.service.hrd.get("github.secret"))        
        return g

    @action()
    def test(self):
        print ("test")

    @action()
    def test2(self):
        print ("test2")        
        print ("$(github.secret)")        

    @action(queue="main")
    def testasync(self):
        print ("testasync")        
        print ("$(github.secret)")                