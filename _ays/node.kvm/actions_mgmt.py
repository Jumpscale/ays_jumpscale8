from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    def init(self,serviceObj,args):

        # ActionsBase.init(self,serviceObj,args)

        # depkey="sshkey"

        # if serviceObj.originator!=None and serviceObj.originator._producers!={} and serviceObj.originator._producers.has_key(depkey):
        #     res=serviceObj.originator._producers[depkey]
        # elif serviceObj._producers!={} and serviceObj._producers.has_key(depkey):
        #     res=serviceObj._producers[depkey]
        # else:
        #     #we need to check if there is a specific consumption specified, if not check generic one            
        #     res = j.atyourservice.findServices(role=depkey)

        # if len(res) == 0:
        #     # not deployed yet
        #     j.events.inputerror_critical("Could not find dependency, please install.\nI am %s, I am trying to depend on %s" % (serviceObj, depkey))
        # elif len(res) > 1:
        #     j.events.inputerror_critical("Found more than 1 dependent ays, please specify, cannot fullfil dependency requirement.\nI am %s, I am trying to depend on %s" % (serviceObj, depkey))
        # else:
        #     serv = res[0]

        # serviceObj.consume(serv)   

        #TRICK TO REUSE ACTION METHOD FROM OTHER AYS
        s=j.atyourservice.getTemplate("jumpscale","node.ssh")
        s.actions.init(serviceObj,args)


        # args["ssh.key.public"]=serv.hrd.get("key.pub")

    def configure(self,serviceObj):
        """
        will create a new virtual machine
        """
        def createVM():
            j.sal.kvm.create(serviceObj.instance,"$(param.baseimage)")

        j.actions.start(retry=2, name="create vm",description='create a virtual machine ($(param.baseimage))', action=createVM, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)

        def getconfig():
            config = j.sal.kvm.getConfig(serviceObj.instance)
            serviceObj.hrd.set("machine.ssh.ip",config.get("bootstrap.ip"))
            serviceObj.hrd.set("machine.ssh.login",config.get("bootstrap.login"))
            serviceObj.hrd.set("machine.ssh.passwd",config.get("bootstrap.passwd"))

        j.actions.start(retry=2, name="get config",description='retreive information about the vm', action=getconfig, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)
        return True


    def removedata(self,serviceObj):
        """
        delete vmachine
        """
        def destroyvm():
            j.sal.kvm.destroy(serviceObj.instance)

        j.actions.start(retry=2, name="destroy vm",description='destroy the virtual machine', action=destroyvm, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)

        return True

    def execute(self,serviceObj,cmd):
        """
        execute over ssh something onto the machine
        """
        j.sal.kvm.execute(name=serviceObj.instance, cmd=cmd)
        return True

    def start(self,serviceObj):
        j.sal.kvm.start(serviceObj.instance)
        return True

    def stop(self,serviceObj):
        j.sal.kvm.stop(serviceObj.instance)
        return True