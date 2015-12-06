from JumpScale import j
# from JumpScale.baselib.atyourservice.ActionsBase import remote
ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def init(self, serviceObj, args):
        depkey = "osis.aio"
        print("## mongodb ##")
        from ipdb import set_trace;set_trace()

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

        args['param.influxdb.client.address']=serv.hrd.get("instance.tcp.addr")
        args['param.influxdb.client.dbname']=serv.hrd.get("instance.db.main")
        args['param.influxdb.client.login']=serv.hrd.get("instance.admin.login")
        args['param.influxdb.client.passwd']=serv.hrd.get("instance.admin.passwd")
        args['param.influxdb.client.port']=serv.hrd.get("instance.tcp.port.service")

        return True

    def prepare(self, serviceObj):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """

        if j.do.TYPE.lower().startswith("osx"):
            res=j.do.execute("brew install mongodb")
            res=j.do.execute("brew list mongodb")
            for line in res[1].split("\n"):
                if line.strip()=="":
                    continue
                if j.do.exists(line.strip()) and line.find("bin/")!=-1:
                    destpart=line.split("bin/")[-1]
                    dest="/opt/mongodb/bin/%s"%destpart
                    j.sal.fs.createDir(j.sal.fs.getDirName(dest))
                    j.do.copyFile(line,dest)
                    j.do.chmod(dest, 0o770)                    

        if j.do.TYPE.lower().startswith("ubuntu"):
            j.do.execute('apt-get purge \'mongo*\' -y')
            j.do.execute('apt-get autoremove -y')            
            j.sal.ubuntu.stopService("mongod")
            j.sal.ubuntu.serviceDisableStartAtBoot("mongod")

        j.sal.fs.createDir("/opt/jumpscale8/var/mongodb/$(service.instance)")

        return True

    def configure(self, serviceObj):
        if serviceObj.hrd.exists("instance.param.replicaset"):
            repset = serviceObj.hrd.get("instance.param.replicaset")
            if repset != "":
                process = serviceObj.hrd.getDictFromPrefix('service.process')['1']
                process['args'] += " --replSet '%s'" % repset
                serviceObj.hrd.set('service.process.1',process)
