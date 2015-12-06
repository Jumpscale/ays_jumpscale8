from JumpScale import j




ActionsBase = j.atyourservice.getActionsBaseClassNode()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        if 'root' != j.sal.ubuntu.whoami():
            path = "/home/%s" % j.sal.ubuntu.whoami()
        else:
            path = "/root"
        ssh_dir = j.sal.fs.joinPaths(path, ".ssh")
        authorized_path = j.sal.fs.joinPaths(ssh_dir, "authorized_keys")

        if not j.sal.fs.exists(path=authorized_path):
            j.sal.fs.createEmptyFile(authorized_path)

        fileName = j.sal.fs.joinPaths(ssh_dir, "%s_read" % serviceObj.instance)
        j.sal.fs.writeFile(filename=fileName, contents=serviceObj.hrd.getStr("key.read"))
        fileName = j.sal.fs.joinPaths(ssh_dir, "%s_write" % serviceObj.instance)
        j.sal.fs.writeFile(filename=fileName, contents=serviceObj.hrd.getStr("key.write"))
