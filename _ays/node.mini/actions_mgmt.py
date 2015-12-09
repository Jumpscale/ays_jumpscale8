from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def __init__(self):
        super(Actions, self).__init__()
        self.enClient = None

    # def input(self, serviceObj, args):
    #     super(Actions, self).input(serviceObj, args)

    #     energyswitch = self._searchDep(serviceObj, 'energyswitch')
    #     serviceObj.consume(energyswitch)
    #     args['energyswitch.addr'] = energyswitch.hrd.getStr('tcp.addr')
    #     args['energyswitch.port'] = energyswitch.hrd.getStr('tcp.port')
    #     args['energyswitch.username'] = energyswitch.hrd.getStr('username')
    #     args['energyswitch.password'] = energyswitch.hrd.getStr('password')


    def start(self, serviceObj):
        es=self._getEnergySwitchClient(serviceObj)
        from IPython import embed
        print ("DEBUG NOW es start")
        embed()
        
        # @TODO use energyswtich

    def stop(self, serviceObj):
        es=self._getEnergySwitchClient(serviceObj)
        from IPython import embed
        print ("DEBUG NOW es stop")
        embed()

    def _getEnergySwitchClient(self, serviceObj):
        energyswitch = self._searchDep(serviceObj, 'energyswitch')
        username=energyswitch.hrd.get("username")
        password=energyswitch.hrd.get("password")
        addr=energyswitch.hrd.get("tcp.addr")
        port=energyswitch.hrd.get("tcp.port")
        powerport_nr="$(energyswitch.port)"
        enClient = j.clients.racktivity.getEnergySwitch(username,password,addr,port)
        return enClient
