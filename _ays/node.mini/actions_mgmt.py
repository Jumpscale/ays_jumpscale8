from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def start(self, serviceObj):
        powerport_nr = "$(energyswitch.port)"
        es = self._getEnergySwitchClient(serviceObj)
        es.power.setPortState(1, int(powerport_nr))

    def stop(self, serviceObj):
        powerport_nr = "$(energyswitch.port)"
        es = self._getEnergySwitchClient(serviceObj)
        es.power.setPortState(0, int(powerport_nr))

    def _getEnergySwitchClient(self, serviceObj):
        energyswitch = self._searchDep(serviceObj, 'energyswitch')
        username = energyswitch.hrd.get("username")
        password = energyswitch.hrd.get("password")
        addr = energyswitch.hrd.get("tcp.addr")
        port = energyswitch.hrd.get("tcp.port")
        enClient = j.clients.racktivity.getEnergySwitch(username,password,addr,port)
        return enClient
