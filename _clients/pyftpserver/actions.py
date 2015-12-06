from JumpScale import j

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

    # def prepare(self,serviceObj):
    #     """
    #     this gets executed before the files are downloaded & installed on appropriate spots
    #     """
    #     j.do.execute('apt-get purge \'nginx*\' -y')
    #     j.do.execute('apt-get autoremove -y')
    #     j.sal.process.killProcessByPort(80)
    #     j.sal.fs.createDir("/var/nginx/cache/fcgi")
    #     j.sal.fs.createDir("/var/log/nginx")
    #     return True

    def configure(self,serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the ays if anything needs to be started
        """
        C="""
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

authorizer = DummyAuthorizer()
authorizer.add_user("$(ro.name)", "$(ro.passwd)", "$(ro.root)", perm="elr")
authorizer.add_user("$(rw.name)", "$(rw.passwd)", "$(rw.root)", perm="elradfmw")

handler = FTPHandler
handler.authorizer = authorizer

server = FTPServer(("0.0.0.0", 21), handler)
server.serve_forever()        
        """
        j.do.writeFile("/opt/pyftpserver/ftpstart.py",C)

