from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

import JumpScale.lib.openvcloud

from JumpScale.baselib.atyourservice.ActionsBaseNode import ActionsBaseNode

class Actions(ActionsBaseNode):

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



    def _getSpaceSecret(self, serviceObj):
        openvcloudclient_hrd = j.application.getAppInstanceHRD("openvcloud_client","$(openvcloud.connection)")
        spacesecret = openvcloudclient_hrd.get("param.secret", '')
        if True or spacesecret == '':
            openvcloudService = j.atyourservice.get(name='openvcloud_client', instance="$(openvcloud.connection)")
            openvcloudService.configure()
            spacesecret = openvcloudService.hrd.get("param.secret")
            if spacesecret == '':
                j.events.opserror_critical('impossible to retreive openvcloud space secret', category='atyourservice')
        return spacesecret

    def getCoudClient(self):
        openvcloudclient_hrd = j.application.getAppInstanceHRD("openvcloud_client","$(openvcloud.connection)")
        return j.tools.openvcloud.get(openvcloudclient_hrd.get('param.apiurl'))

    def configure(self, serviceObj):
        """
        create a vm on openvcloud
        """
        def createmachine():
            cloudCl = self.getCoudClient()
            spacesecret = self._getSpaceSecret(serviceObj)
            _, sshkey = self.getSSHKey(serviceObj)

            machineid, ip, port = cloudCl.createMachine(spacesecret, serviceObj.instance, memsize="$(memsize)",
                ssdsize=$(ssdsize), vsansize=0, description='', imagename="$(imagename)", elete=False, sshkey=sshkey)

            serviceObj.hrd.set("machine.id",machineid)
            serviceObj.hrd.set("ip",ip)
            serviceObj.hrd.set("ssh.port",port)

        j.actions.start(retry=1, name="createmachine", description='createmachine', cmds='', action=createmachine,
                        actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)

        # only do the rest if we want to install jumpscale
        if serviceObj.hrd.getBool('jumpscale'):
            self.installJumpscale(serviceObj)

    def removedata(self, serviceObj):
        """
        delete vmachine
        """
        openvcloudclient_hrd = j.application.getAppInstanceHRD("openvcloud_client","$(openvcloud.connection)")
        spacesecret = openvcloudclient_hrd.get("param.secret")
        cloudCl = self.getCoudClient()
        cloudCl.deleteMachine(spacesecret, serviceObj.instance)

        return True

    def start(self, serviceObj):
        if serviceObj.hrd.get('machine.id', '') != '':
            cloudCl = self.getCoudClient()
            spacesecret = self._getSpaceSecret(serviceObj)
            cloudCl.startMachine(spacesecret, serviceObj.instance)

    def stop(self, serviceObj):
        if serviceObj.hrd.get('machine.id') != '':
            cloudCl = self.getCoudClient()
            spacesecret = self._getSpaceSecret(serviceObj)
            cloudCl.stopMachine(spacesecret, serviceObj.instance)