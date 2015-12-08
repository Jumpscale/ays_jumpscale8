from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def __init__(self):
        super(Actions, self).__init__()
        self.enClient = None

    def searchDep(self, serviceObj, depkey):
        if serviceObj._producers != {} and depkey in serviceObj._producers:
            dep = serviceObj._producers[depkey]
        else:
            dep = j.atyourservice.findServices(role=depkey)

        if len(dep) == 0:
            j.events.inputerror_critical("Could not find dependency, please install.\nI am %s, I am trying to depend on %s" % (serviceObj, depkey))
        elif len(dep) > 1:
            j.events.inputerror_critical("Found more than 1 dependent ays, please specify, cannot fullfil dependency requirement.\nI am %s, I am trying to depend on %s" % (serviceObj, depkey))
        else:
            serv = dep[0]
        return serv

    def init(self, servivceObj, args):
        super(Actions, self).init(servivceObj, args)

        energyswitch = self.searchDep(servivceObj, 'energyswitch')
        servivceObj.consume(energyswitch)
        args['energyswitch.addr'] = energyswitch.hrd.getStr('tcp.addr')
        args['energyswitch.port'] = energyswitch.hrd.getStr('tcp.port')
        args['energyswitch.username'] = energyswitch.hrd.getStr('username')
        args['energyswitch.password'] = energyswitch.hrd.getStr('password')

    def install(self, servivceObj):
        pass
        # @TODO

    def start(self, servivceObj):
        pass
        # @TODO use energyswtich

    def stop(self, servivceObj):
        pass
        # @TODO use energyswtich

    def getEnergySwitchClien(self, servivceObj):
        if self.enClient is None:
            self.enClient = j.clients.racktivity.getEnergySwitch(
                '$(energyswitch.username)',
                '$(energyswitch.password)',
                '$(energyswitch.addr)',
                '$(energyswitch.port)')
        return self.enClient
