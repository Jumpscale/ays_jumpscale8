from JumpScale import j


class Actions(ActionsBaseMgmt):


    def input(self,name,role,instance,args={}):

        if "g8.account" not in args or args["g8.account"].strip()=="":
            args['g8.account']=args["g8.login"]

        return args


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
