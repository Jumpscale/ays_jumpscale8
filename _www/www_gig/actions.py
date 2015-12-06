from JumpScale import j
import time
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

    def prepare(self,serviceObj):
        """
        this gets executed before the files are downloaded & installed on appropriate spots
        """
        instance='$(portal.instance)'

        path="$base/apps/portals/%s"%instance
        if j.sal.fs.isLink(path):
            j.sal.fs.unlink(path)

        ays = j.atyourservice.findServices("jumpscale","portal")
        if not ays.isInstalled(instance=instance):
            j.events.inputerror_critical("Could not find portal instance with name: %s, please install"%instance)

#        if j.sal.nettools.tcpPortConnectionTest("localhost",9999)==False:
#            j.events.opserror_critical("could not find redis on port 9999",category="wwwjumpscale.install")

 #       j.sal.fs.removeDirTree("$base/apps/portals/%s/base/test__taskmanager/"%instance)
        return True

    def configure(self,serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the ays if anything needs to be started
        """
        # j.application.config.applyOnDir("$(param.base)/cfg",filter=None, changeFileName=True,changeContent=True,additionalArgs={})  

        return True

    # def start(self,serviceObj):
    #     #start postgresql in background
    #     if j.sal.nettools.tcpPortConnectionTest("localhost",3306):
    #         return

    #     import JumpScale.sal.screen

    #     cmd="/opt/mariadb/bin/postgresqld --basedir=/opt/mariadb --datadir=/opt/mariadb/data --plugin-dir=/opt/mariadb/lib/plugin/ --user=root --console --verbose"
    #     j.sal.screen.createSession("servers",["mariadb"])
    #     j.sal.screen.executeInScreen(sessionname="servers", screenname="mariadb", cmd=cmd, wait=0, cwd=None, env=None, user='root', tmuxuser=None)

    #     #now wait till we can access the port
    #     res=j.sal.nettools.waitConnectionTest("localhost",3306,2)
    #     if res==False:
    #         j.events.inputerror_critical("mariadb did not become active, check in byobu","ays.install.mariadb.startup")

    def stop(self,serviceObj):
        """
        if you want a gracefull shutdown implement this method
        a uptime check will be done afterwards (local)
        return True if stop was ok, if not this step will have failed & halt will be executed.
        """        
        return True
        # if self.check_down_local(hrd):
        #     return True
        # else:
        #     j.events.opserror_critical("Cannot stop %s."%self.jp,"ays.stop")




