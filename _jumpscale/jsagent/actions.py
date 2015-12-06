from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def init(self, serviceObj, args):
        super(Actions, self).init(serviceObj, args)

        if 'agentcontroller_client' not in serviceObj._producers:
            j.events.opserror_critical(msg="can't find agentcontroller_client, need to consume agentcontroller_client", category="jsagent.init")

        if 'osis_client' not in serviceObj._producers:
            j.events.opserror_critical(msg="can't find osis_client, need to consume osis_client", category="jsagent.init")

        mongodb_instance = serviceObj._producers['agentcontroller_client'][0].instance
        osis_client = serviceObj._producers['osis_client'][0].instance
        args['agentcontroller.connection'] = mongodb_instance
        args['osis.connection'] = osis_client

    def prepare(self, serviceObj):
        hpath = j.sal.fs.joinPaths(j.dirs.hrd, 'grid.hrd')
        hrd = j.data.hrd.get(hpath)
        hrd.set('id', serviceObj.hrd.get('grid.id'))
        hrd.set('node.id', '0')
        hrd.set('node.machineguid', j.application.getUniqueMachineId())
        hrd.set('node.roles', serviceObj.hrd.getStr('grid.node.roles').split(','))
        hrd.save()

        # reload system config / whoAmI
        j.application.loadConfig()

    def start(self, *args, **kwargs):
        result = ActionsBase.start(self, *args, **kwargs)
        j.application.loadConfig()
        j.application.initWhoAmI(True)
        return result
