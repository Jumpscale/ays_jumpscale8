from JumpScale import j
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

    def prepare(self, serviceObj):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """
        def createLogDir():
            path = j.sal.fs.joinPaths(j.dirs.logDir, "openvpn")
            if j.sal.fs.exists(path):
                j.sal.fs.removeDirTree(path)
            j.sal.fs.createDir(path)
        j.actions.start(description='create Logging Directory', action=createLogDir, name='createLogDir', serviceObj=serviceObj)

        return True

    def configure(self, serviceObj):
        def createConf():
            serviceObj.hrd.applyOnFile("/opt/openvpn/etc/server.conf")
            j.application.config.applyOnFile("/opt/openvpn/etc/server.conf")

            serviceObj.hrd.applyOnFile("/opt/openvpn/etc/client.conf")
            j.application.config.applyOnFile("/opt/openvpn/etc/client.conf")
        j.actions.start(description='create config files', name='createConf', action=createConf, serviceObj=serviceObj)

        def writeVarsFile():
            serviceObj.hrd.applyOnFile("/opt/openvpn/easy-rsa/vars")
        j.actions.start(description='writeVarsFile', action=writeVarsFile, name='writeVarsFile', serviceObj=serviceObj)

        def generateCerts():
            script = "/bin/bash -c 'cd /opt/openvpn/easy-rsa; source vars; ./clean-all'"
            j.do.executeInteractive(script)

            script = "/bin/bash -c 'cd /opt/openvpn/easy-rsa; source vars; ./build-ca'"
            j.do.executeInteractive(script)

            script = "/bin/bash -c 'cd /opt/openvpn/easy-rsa; source vars; ./build-key-server server'"
            j.do.executeInteractive(script)

            script = "/bin/bash -c 'cd /opt/openvpn/easy-rsa; source vars; ./build-key client'"
            j.do.executeInteractive(script)

            script = "/bin/bash -c 'cd /opt/openvpn/easy-rsa; source vars; ./build-dh'"
            j.do.executeInteractive(script)

            files = ['ca.crt', 'server.key', 'server.crt','client.key', 'client.crt', 'dh2048.pem']
            for f in files:
                source = j.sal.fs.joinPaths('/opt/openvpn/easy-rsa/keys', f)
                dest = j.sal.fs.joinPaths('/opt/openvpn/etc/', f)
                j.sal.fs.copyFile(source, dest)
        j.actions.start(description='Create the CA (Root certificate)', action=generateCerts, name='generateCerts', serviceObj=serviceObj)

    def removedata(self, serviceObj):
        script = "/bin/bash -c 'source vars; ./clean-all'"
        j.do.execute(script, cwd='/opt/openvpn/easy-rsa')
