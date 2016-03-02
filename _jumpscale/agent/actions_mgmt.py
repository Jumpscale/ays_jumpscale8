from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def __init__(self, service):
        super(Actions, self).__init__(service)
        self.service = service
        self._cuisine = None

    @property
    def cuisine(self):
        if not self._cuisine:
            self._cuisine = self.service.parent.action_methods_mgmt.getExecutor().cuisine
        return self._cuisine

    def install(self):
        nid = self.service.parent.hrd.get("machine.id",None)
        self.cuisine.builder.core(nid)


    def start(self):
        pass
