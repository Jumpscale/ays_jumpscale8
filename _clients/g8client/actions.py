from JumpScale import j


class Actions():


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
        return j.clients.openvcloud.get("$(g8.url)", '$(g8.login)', '$(g8.password)')
