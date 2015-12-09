from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassNode()


class Actions(ActionsBase):

    def install(self, serviceObj):
        cl=j.tools.cuisine.local
        cl.dir_ensure("/etc/ays/local")