from JumpScale import j


class Actions(ActionsBaseMgmt):
    def _findWeavePeer(self):
        services = self.service.aysrepo.findServices(role='dockerhost')
        for service in services:
            if self.service.instance == self.service.instance or not self.service.hrd.exists('machine.publicip'):
                continue
            ip = self.service.hrd.getStr('machine.publicip')
            if ip:
                return ip
        return None

    def install(self):
        executor = self.service.parent.getExecutor()
        executor.cuisine.apps.weave.build(peer=self._findWeavePeer())
