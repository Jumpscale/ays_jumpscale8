from JumpScale import j

ActionsBase = service.aysrepo.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def getClient(self):
        url = service.hrd.getStr('url')
        login = service.hrd.getStr('login')
        passwd = service.hrd.getStr('password')
        return j.clients.skydns.get(url, login, passwd)
