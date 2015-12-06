from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        j.remote.avahi.registerService(servicename='$(name)',
                                       port='$(port)',
                                       type='$(type)')

    def removedata(self, serviceObj):
        j.remote.avahi.removeService(servicename='$(name)')
