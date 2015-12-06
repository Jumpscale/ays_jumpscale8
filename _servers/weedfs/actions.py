from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

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

    def prepare(self,serviceObj):
        j.do.createDir("/var/weedfs")

    def configure(self,serviceObj):

        if not j.sal.fs.exists("$(param.storagelocation)"):
            j.sal.fs.createDir("$(param.storagelocation)")
        storlocs=j.do.listDirsInDir("$(param.storagelocation)")
        for storloc in storlocs:
            counter=int(j.do.getBaseName(storloc))
            pd={"args":"","name":'$(service.name)_voldr_%s'%counter,'prio':10,'cwd':'$(param.base)','timeout_start':10,'timeout_stop':10,'startupmanager':'tmux','filterstr':''}
            pd["ports"]=[9333+counter]
            pd["cmd"]="'./weed volume -port=%s -dir=%s -max=5 -ip=127.0.0.1 -ip.bind=127.0.0.1 -whiteList=127.0.0.1 -mserver=localhost:9333'"%(9333+counter,storloc)

            serviceObj.hrd.set("process.%s"%(counter+1),pd,ttype="dict")


    def build(self,serviceObj):
        """
        instructions how to build the package
        build to /opt/luajit
        """
        j.sal.ubuntu.checkInstall(["mercurial"], "hg")
        cmd="""
set -ex
. /opt/go/goenv.sh
cd /opt/go/myproj
go get github.com/chrislusf/weed-fs/go/weed
"""
        print(cmd)
        j.actions.start(retry=1, name="weedfsbuild",description='', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)

        source="/opt/go/myproj/bin/weed"
        j.do.createDir("/opt/weedfs")
        j.do.copyFile(source,"/opt/weedfs/weed")