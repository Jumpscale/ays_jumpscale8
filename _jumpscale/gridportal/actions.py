from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def init(self, serviceObj, args):
        super(Actions, self).init(serviceObj, args)

        # need to know where to put the file
        portalInstance = j.atyourservice.findServices(role='portal', parent=serviceObj.parent, first=True).instance
        args['portal.instance'] = portalInstance