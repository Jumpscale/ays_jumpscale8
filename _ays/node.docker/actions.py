from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def __init__(self):
        self._client = None

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

        
        if args["jumpscale.sharecode"]==True or args["jumpscale.sharecode"]==1 or args["jumpscale.sharecode"]=="1":
            args["jumpscale.reset"]=False 


    def configure(self, serviceObj):
        """
        will install create a docker container
        """

        pubkey=serviceObj.hrd.getStr("ssh.key.public")
        ports = serviceObj.hrd.getStr('docker.portsforwards', None)
        volumes = serviceObj.hrd.getStr('docker.volumes', None)
        installJS = serviceObj.hrd.getBool('jumpscale', False)

        port=j.sal.docker.create(name=serviceObj.instance, stdout=True, base="$(docker.image)",
                              ports=ports, vols=volumes,sshpubkey=pubkey,
                              jumpscale=installJS, sharecode=serviceObj.hrd.getBool('jumpscale.sharecode'),jumpscalebranch="$(jumpscale.branch)")

        serviceObj.hrd.set("ssh.port", port)
        _, ip = j.system.net.getDefaultIPConfig()
        serviceObj.hrd.set("node.tcp.addr", ip)

        j.do.loadSSHKeys()

        #TRICK TO REUSE ACTION METHOD FROM OTHER AYS
        s=j.atyourservice.getTemplate("jumpscale","node.ssh")
        s.actions.configure(serviceObj)

    def removedata(self, serviceObj):
        """
        delete docker container
        """
        j.sal.docker.destroy(serviceObj.instance)
        return True

    def start(self, serviceObj):
        j.sal.docker.restart(serviceObj.instance)

    def stop(self, serviceObj):
        j.sal.docker.stop(serviceObj.instance)

