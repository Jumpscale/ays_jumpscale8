from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def prepare(self, serviceObj):
        dataDir = j.sal.fs.joinPaths(j.dirs.varDir, 'consul')
        j.sal.fs.createDir(dataDir)

    def build(self, serviceObj):
        go = j.atyourservice.getService(name='go')
        gopath = go.hrd.getStr('instance.gopath')

        go.actions.buildProjectGodep(go, 'https://github.com/EmileVauge/traefik', generate=True)
        binDest = j.sal.fs.joinPaths('/opt/code/git/binary', 'traefik')
        j.sal.fs.createDir(j.sal.fs.joinPaths(binDest))

        binSource = j.sal.fs.joinPaths(gopath, 'bin/traefik')
        j.sal.fs.copyFile(binSource, binDest)
