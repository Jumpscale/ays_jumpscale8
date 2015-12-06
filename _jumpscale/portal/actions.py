from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):


    def prepare(self, serviceObj):
        """
        this gets executed before the files are downloaded & installed on appropriate spots
        """
        print("prepare portal")        

        #@todo does not work, need to fix, something with no executing in ssh remote
        # j.sal.ubuntu.updatePackageMetadata()
        # j.sal.ubuntu.install('graphviz')

        # j.do.executeInteractive("apt-get update -y")
        j.do.executeInteractive("apt-get install graphviz -y")
        print("done prepare")
        return True

    def configure(self, serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the ays if anything needs to be started
        """
        cmd = 'jsuser list'
        res = j.do.execute(cmd, dieOnNonZeroExitCode=False)[1]
        for line in res.splitlines():
            if line.find('admin') != -1:
                return True

        cmd='jsuser add -d admin:$(param.portal.rootpasswd):admin:fakeemail.test.com:jumpscale'
        j.do.execute(cmd, dieOnNonZeroExitCode=False)

        # ini.write()
        return True

