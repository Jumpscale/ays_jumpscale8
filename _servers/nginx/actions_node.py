from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassNode()


class Actions(ActionsBase):

    def prepare(self, serviceObj):
        # hack for sandboxed nginx to start properly
        j.sal.fs.createDir(j.sal.fs.joinPaths('/var', 'lib', 'nginx'))
        # make sur required log directory exists
        logPath = j.sal.fs.joinPaths('/var', 'log', 'nginx')
        if not j.sal.fs.exists(logPath):
            j.sal.fs.createDir(logPath)
