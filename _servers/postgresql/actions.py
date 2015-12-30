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

    def prepare(self, serviceObj):
        """
        this gets executed before the files are downloaded & installed on appropriate spots
        """
        try:
            j.sal.ubuntu.createUser("postgres", passwd=j.data.idgenerator.generateGUID(),
                                            home="/home/postgresql", creategroup=True)
        except Exception:
            pass

        j.sal.process.killProcessByPort("$(param.port)")
        j.sal.fs.createDir("/tmp/postgres")
        j.sal.fs.createDir("/var/run/postgresql")
        j.system.unix.chown('/var/run/postgresql', 'postgres', 'postgres')

        return True

    def configure(self, serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the ays if anything needs to be started
        """
        # j.application.config.applyOnDir("$(param.base)/cfg",filter=None, changeFileName=True,changeContent=True,additionalArgs={})

        if j.sal.fs.exists(path="$(service.datadir)"):
            # Already configured once. Nothing to do here.
            return

        j.sal.fs.createDir("$(service.datadir)")
        j.sal.fs.chown(path="$(service.param.base)", user="postgres")
        j.sal.fs.chown(path="$(service.datadir)", user="postgres")
        j.sal.fs.chmod("$(service.datadir)", 0o777)
        j.sal.fs.chmod("/tmp", 0o777)

        cmd = "su -c '$(service.param.base)/bin/initdb -D $(service.datadir)' postgres"
        j.sal.process.executeWithoutPipe(cmd)

        def replace(path, newline, find):
            lines = j.sal.fs.fileGetContents(path)
            out = ""
            found = False
            for line in lines.split("\n"):
                if line.find(find) != -1:
                    line = newline
                    found = True
                out += "%s\n" % line
            if found is False:
                out += "%s\n" % newline
            j.sal.fs.writeFile(filename=path, contents=out)

        replace("$(service.datadir)/pg_hba.conf",
                "host    all             all             0.0.0.0/0               md5", "0.0.0.0/0")
        replace("$(service.datadir)/postgresql.conf",
                "unix_socket_directories = '/tmp,/var/run/postgresql'    # comma-separated list of directories ", "unix_socket_directories")

        j.sal.fs.createDir("/var/log/postgresql")

        self.start(serviceObj)
        time.sleep(2)

        cmd = "cd $(service.param.base)/bin;./psql -U postgres template1 -c \"alter user postgres with password '$param.rootpasswd)';\" -h localhost"
        j.do.execute(cmd)

        # self.stop()

        return True


    def stop(self, serviceObj):
        """
        if you want a gracefull shutdown implement this method
        a uptime check will be done afterwards (local)
        return True if stop was ok, if not this step will have failed & halt will be executed.
        """
        # No process actually running
        if not j.sal.process.getPidsByPort("$(param.port)"):
            return

        cmd = "sudo -u postgres $(service.param.base)/bin/pg_ctl -D /var/jumpscale/postgresql stop  -m fast"
        # print (cmd)
        rc, out, err = j.do.execute(
            cmd, dieOnNonZeroExitCode=False, outputStdout=False, outputStderr=True, timeout=5)
        if rc > 0:
            if rc == 999:
                cmd = "sudo -u postgres $(service.param.base)/bin/pg_ctl -D /var/jumpscale/postgresql stop  -m immediate"
                rc, out, err = j.do.execute(
                    cmd, dieOnNonZeroExitCode=False, outputStdout=False, outputStderr=True, timeout=5)
            else:
                raise RuntimeError("could not stop %s" % serviceObj)

