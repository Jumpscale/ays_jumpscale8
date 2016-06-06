from JumpScale import j


class Actions(ActionsBaseMgmt):
    def init(self, service):
        return True

    def getSender(self, service):
        login = service.hrd.getStr('smtp.login')
        password = service.hrd.getStr('smtp.passwd')
        server = service.hrd.getStr('smtp.server')
        port = service.hrd.getStr('smtp.port')
        return j.tools.email.getSender(login, password, server, port)
