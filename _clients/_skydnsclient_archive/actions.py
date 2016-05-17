from JumpScale import j


class Actions(ActionsBaseMgmt):

    def getClient(self):
        url = self.service.hrd.getStr('url')
        login = self.service.hrd.getStr('login')
        passwd = self.service.hrd.getStr('password')
        return j.clients.skydns.get(url, login, passwd)
