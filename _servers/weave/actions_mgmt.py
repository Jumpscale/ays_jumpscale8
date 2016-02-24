from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):
    def _findWeavePeer(self):
        services = j.atyourservice.findServices(role='dockerhost')
        for service in services:
            if service.instance == self.service.instance or not service.hrd.exists('machine.publicip'):
                continue
            ip = service.hrd.getStr('machine.publicip')
            if ip:
                return ip
        return None

    def install(self):
        executor = self.service.parent.getExecutor()
        executor.cuisine.builder.weave(peer=self._findWeavePeer())
