from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()




class Actions(ActionsBase):


    def prepare(self,serviceObj):
        """
        """

        if j.do.TYPE.lower().startswith("ubuntu64"):
            # j.sal.ubuntu.downloadInstallDebPkg("https://s3.amazonaws.com/influxdb/influxdb_0.9.2-rc1_amd64.deb",minspeed=50)
            # for path in j.sal.ubuntu.listFilesPkg("influxdb",regex=".*\/versions\/.*\/infl.*"):
            #     #find the files which have been installed
            #     j.do.copyFile(path,"$(service.param.base)",skipIfExists=True)            
            url="https://dl.bintray.com/mitchellh/consul/0.5.2_linux_amd64.zip"
            j.do.download(url, to='/tmp/consul.zip', overwrite=True, retry=3, timeout=0, login='', passwd='', minspeed=0, multithread=False, curl=False)
            j.do.execute("cd /tmp;rm -f consul;unzip /tmp/consul.zip;mkdir -p /opt/consul;cp consul /usr/local/bin/;rm -rf consul*")

            url="https://dl.bintray.com/mitchellh/consul/0.5.2_web_ui.zip"
            j.do.download(url, to='/tmp/consulweb.zip', overwrite=True, retry=3, timeout=0, login='', passwd='', minspeed=0, multithread=False, curl=False)
            j.do.execute("cd /tmp;rm -rf /tmp/dist;unzip /tmp/consulweb.zip")

            j.do.copyTree("/tmp/dist/","/opt/consul/web")

            j.do.delete("/tmp/dist")            
            
            j.do.createDir("/opt/consul/config")

        else:
          raise RuntimeError("not supported")

        return True

    def configure(self,service):

        CONFIG="""
        {
          "encrypt": "$gossipkey",
          "datacenter": "$(datacenter.id)",
          "data_dir": "/opt/consul/data",
          "log_level": "INFO",
          "node_name": "$(datacenter.id)",
          "server": true
        }
        """

        if service.hrd.get("gossip.key",default="")=="":
            rc,key,err=j.do.execute("consul keygen")
            key=key.strip()
            service.hrd.set("gossip.key",key)

        CONFIG=CONFIG.replace("$gossipkey",service.hrd.get("gossip.key"))

        path="/opt/consul/config/main.json"
        j.do.writeFile(path,CONFIG)

        service.hrd.applyOnDir("/opt/consul/config")
        
        service.hrd

        

    # def configure(self, service):
    #     cfg = j.dirs.replaceTxtDirVars(CONFIG, additionalArgs={})
    #     j.do.writeFile("$(service.param.base)/cfg/config.toml", cfg)

    # def build(self,serviceObj):

    #     #to reset the state use ays reset -n ...

    #     j.sal.ubuntu.check()
    #     #@todo