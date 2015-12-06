from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassNode()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        version = j.sal.ubuntu.version()
        major, minor = version.split('.')
        if int(major) >= 15:
            j.sal.process.executeWithoutPipe("sudo systemctl unmask docker.service")
            j.sal.process.executeWithoutPipe("sudo systemctl unmask docker.socket")
            j.sal.process.executeWithoutPipe("sudo service docker restart")

        return True

    def start(self, serviceObj):
        j.do.execute('service docker start', dieOnNonZeroExitCode=False)

    def stop(self, serviceObj):
        j.do.execute('service docker stop', dieOnNonZeroExitCode=False)