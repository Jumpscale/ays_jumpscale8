from JumpScale import j
import time
import socket
import fcntl
import struct

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def init(self, serviceObj, args):
        super(Actions, self).init(serviceObj, args)

        depkey = "statsd-master"

        if serviceObj.originator is not None and serviceObj.originator._producers != {} and depkey in serviceObj.originator._producers:
            res = serviceObj.originator._producers[depkey]
        elif serviceObj._producers != {} and depkey in serviceObj._producers:
            res = serviceObj._producers[depkey]
        else:
            # we need to check if there is a specific consumption specified, if not check generic one
            res = j.atyourservice.findServices(role=depkey)

        if len(res) == 0:
            # not deployed yet
            j.events.inputerror_critical("Could not find dependency, please install.\nI am %s, I am trying to depend on %s" % (serviceObj, depkey))
        elif len(res) > 1:
            j.events.inputerror_critical("Found more than 1 dependent ays, please specify, cannot fullfil dependency requirement.\nI am %s, I am trying to depend on %s" % (serviceObj, depkey))
        else:
            serv = res[0]

        serviceObj.consume(serv)

        args['statsd.master.host'] = serv.hrd.getStr('tcp.addr')

    def configure(self, serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the ays if anything needs to be started
        """
        hrd = serviceObj.hrd
        configsamplepath = j.sal.fs.joinPaths('/opt/', 'statsd-collector', 'CollectorConfig.js')
        configpath = j.sal.fs.joinPaths('/opt/', 'statsd-collector', 'statsd.collector.conf.js')
        if not j.sal.fs.exists(configpath):
            j.sal.fs.createEmptyFile(configpath)

        j.sal.fs.copyFile(configsamplepath, configpath)
        hrd.applyOnFile(configpath)
