from JumpScale import j

ActionsBase = self.service.aysrepo.getActionsBaseClassMgmt()


class Actions(ActionsBase):
    def _findWeavePeer(self):
        services = self.service.aysrepo.findServices(role='dockerhost')
        for service in services:
            if service.instance == self.service.instance or not service.hrd.exists('machine.publicip'):
                continue
            ip = service.hrd.getStr('machine.publicip')
            if ip:
                return ip
        return None

    def install(self):
        executor = self.service.parent.getExecutor()
        executor.cuisine.apps.weave.build(peer=self._findWeavePeer())
