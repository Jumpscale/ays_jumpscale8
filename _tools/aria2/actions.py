from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def prepare(self,serviceObj):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """

        if j.do.TYPE.lower().startswith("osx"):
            res=j.do.execute("brew install aria2")

        if j.do.TYPE.lower().startswith("ubuntu64"):
            j.sal.ubuntu.install("aria2")
                j.do.copyFile(path,"$(service.param.base)",skipIfExists=True) 

        j.do.download("https://github.com/ziahamza/webui-aria2/archive/master.zip","/opt/aria2webui/master.zip")           

        return True

