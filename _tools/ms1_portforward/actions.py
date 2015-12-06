from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        openvcloudClientHRD = j.application.getAppInstanceHRD('openvcloud_client', '$(param.openvcloud.connection)')
        spacesecret = openvcloudClientHRD.getStr('param.secret')

        protocol = serviceObj.hrd.getStr('param.protocol')
        spacePort = serviceObj.hrd.getInt('param.space.port')
        vmName = serviceObj.hrd.getStr('param.vm.name')
        vmPort = serviceObj.hrd.getInt('param.vm.port')

        if protocol.lower() == 'tcp':
            j.tools.openvcloud.createTcpPortForwardRule(spacesecret, vmName, vmPort, pubipport=spacePort)
        elif protocol.lower() == 'udp':
            j.tools.openvcloud.createUdpPortForwardRule(spacesecret, vmName, vmPort, pubipport=spacePort)

        return True

    def removedata(self, serviceObj):
        openvcloudClientHRD = j.application.getAppInstanceHRD('openvcloud_client', '$(param.openvcloud.connection)')
        spacesecret = openvcloudClientHRD.getStr('param.secret')

        protocol = serviceObj.hrd.getStr('param.protocol')
        spacePort = serviceObj.hrd.getInt('param.space.port')
        vmName = serviceObj.hrd.getStr('param.vm.name')
        vmPort = serviceObj.hrd.getInt('param.vm.port')

        if protocol.lower() == 'tcp':
            j.tools.openvcloud.deleteTcpPortForwardRule(spacesecret, vmName, vmPort, pubipport=spacePort)
        elif protocol.lower() == 'udp':
            j.tools.openvcloud.deleteUdpPortForwardRule(spacesecret, vmName, vmPort, pubipport=spacePort)

        return True
