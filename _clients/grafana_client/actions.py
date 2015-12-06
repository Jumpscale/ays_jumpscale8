from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def init(self, serviceObj, args):
        super(Actions, self).init(serviceObj, args)

        depkey = "grafana"

        if serviceObj.originator is not None and serviceObj.originator._producers != {} and depkey in serviceObj.originator._producers:
            res = serviceObj.originator._producers[depkey]
        elif serviceObj._producers != {} and depkey in serviceObj._producers:
            res = serviceObj._producers[depkey]
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

        addr = args['tcp.addr'] if 'tcp.addr' in args is not None else 'localhost'
        args['param.url'] = 'http://%s:%s' % (addr, serv.hrd.getStr('tcp.port.service'))
        args['param.username'] = 'admin'
        args['param.password'] = serv.hrd.getStr('param.password')
