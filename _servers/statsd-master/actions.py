from JumpScale import j
import time
import socket
import fcntl
import struct

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def init(self, serviceObj, args):
        super(Actions, self).init(serviceObj, args)

        if serviceObj.parent and serviceObj.parent.role == 'node':
            args['tcp.addr'] = serviceObj.parent.hrd.getStr('node.tcp.addr')
        else:
            args['tcp.addr'] = 'localhost'

    def configure(self, serviceObj):
        if 'influxdb_client' not in serviceObj.producers:
            j.events.opserror_critical(msg="influxdb_client not found in producers, need to consume a influxdb_client", category="statds-master.init")

        hrd = serviceObj.producers['influxdb_client'][0].hrd
        template = {
            'host': hrd.get('param.influxdb.client.address'),
            'port': hrd.get('param.influxdb.client.port'),
            'login': hrd.get('param.influxdb.client.login'),
            'passwd': hrd.get('param.influxdb.client.passwd'),
            'dbname': hrd.get('param.influxdb.client.dbname')
        }

        configsamplepath = j.sal.fs.joinPaths('/opt/', 'statsd-master', 'MasterConfig.js')
        configpath = j.sal.fs.joinPaths('/opt/', 'statsd-master', 'statsd.master.conf.js')
        if not j.sal.fs.exists(configpath):
            j.sal.fs.createEmptyFile(configpath)

        j.sal.fs.copyFile(configsamplepath, configpath)
        hrd.applyOnFile(configpath, template)
