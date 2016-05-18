from JumpScale import j


class Actions(ActionsBaseMgmt):


    def input(self,service,name,role,instance,serviceargs):

        if "g8.account" not in serviceargs or serviceargs["g8.account"].strip()=="":
            serviceargs['g8.account']=serviceargs["g8.login"]

        return serviceargs


    def init(self):
        pass

    def getClient(self):
        """
        return client towards g8 master
        """
        url = service.hrd.getStr('g8.url')
        login = service.hrd.getStr('g8.login')
        password = service.hrd.getStr('g8.password')
        return j.clients.openvcloud.get(url, login, password)
