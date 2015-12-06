from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):
    """
    process for install
    -------------------
    step1: prepare actions
    step2: check_requirements action
    step3: download files & copy on right location (hrd info is used)
    step4: configure action
    step5: check_uptime_local to see if process stops  (uses timeout $process.stop.timeout)
    step5b: if check uptime was true will do stop action and retry the check_uptime_local check
    step5c: if check uptime was true even after stop will do halt action and retry the check_uptime_local check
    step6: use the info in the hrd to start the application
    step7: do check_uptime_local to see if process starts
    step7b: do monitor_local to see if package healthy installed & running
    step7c: do monitor_remote to see if package healthy installed & running, but this time test is done from central location
    """
    def init(self, serviceObj, args):
        super(Actions, self).init(serviceObj, args)

        depkey = "agentcontroller"

        if serviceObj.originator!=None and serviceObj.originator._producers!={} and depkey in serviceObj.originator._producers:
            res=serviceObj.originator._producers[depkey]
        elif serviceObj._producers!={} and depkey in serviceObj._producers:
            res=serviceObj._producers[depkey]
        else:
            #we need to check if there is a specific consumption specified, if not check generic one
            res = j.atyourservice.findServices(role=depkey)

        if len(res) == 0:
            # not deployed yet
            j.events.inputerror_critical("Could not find dependency, please install.\nI am %s, I am trying to depend on %s" % (serviceObj, depkey))
        elif len(res) > 1:
            j.events.inputerror_critical("Found more than 1 dependent ays, please specify, cannot fullfil dependency requirement.\nI am %s, I am trying to depend on %s" % (serviceObj, depkey))
        else:
            serv = res[0]

        serviceObj.consume(serv)

        args['agentcontroller.client.addr'] = serv.hrd.get('tcp.addr')
        args['agentcontroller.client.port'] = serv.hrd.get('tcp.port.service')
        args['agentcontroller.client.login'] = 'node'
        args['agentcontroller.client.passwd'] = ''

        return True



