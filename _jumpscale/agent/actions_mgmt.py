from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def __init__(self, service):
        super(Actions, self).__init__(service)
        self.service = service
        self._cuisine = None

    def install(self):        
        machine = self.parent.actions_mgmt.getMachine()
        executor = machine.get_ssh_connection()
        executor.cuisine.builder.core(j.application.whoAmI.gid, machine.id)

        executor.cuisine.bash.addPath('/opt/jumpscale8/bin')
        executor.cuisine.builder._startCore(j.application.whoAmI.gid, machine.id)
