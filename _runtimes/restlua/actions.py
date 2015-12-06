from JumpScale import j
import JumpScale.baselib.swaggergen

ActionsBase=j.packages.getActionsBaseClass()

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
        """
        this gets executed before the files are downloaded & installed on appropriate spots
        """
        return True

    def configure(self,serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the ays if anything needs to be started
        """
        dest=j.sal.fs.joinPaths("$(system.paths.base)/apps/restlua/",)

        def createServerAndClient():
            j.sal.fs.createDir(dest)
            server = j.sal.fs.joinPaths(dest, 'server.lua')
            client = j.sal.fs.joinPaths(dest, 'client.spore')
            spec = serviceObj.hrd.get('param.spec')
            j.tools.swaggerGen.loadSpec(spec)
            j.tools.swaggerGen.generate("$(param.baseurl)",server,client)
            serviceObj.hrd.set('param.port',j.tools.swaggerGen.server['port'])

        j.actions.start(retry=1, name="createServerAndClient",description='createServerAndClient', cmds='', action=createServerAndClient, \
            actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)

    def removedata(self):
        j.sal.fs.removeDirTree(dest)



