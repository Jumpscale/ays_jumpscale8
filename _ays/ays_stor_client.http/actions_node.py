from JumpScale import j




ActionsBase = j.atyourservice.getActionsBaseClassNode()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        pass
        # if 'root' != j.sal.ubuntu.whoami():
        #     path = "/home/%s" % j.sal.ubuntu.whoami()
        # else:
        #     path = "/root"
        # ssh_dir = j.sal.fs.joinPaths(path, ".ssh")
        #
        # if not j.sal.fs.exists(path=authorized_path):
        #     j.sal.fs.createEmptyFile(authorized_path)
        #
        # for stor, key in serviceObj.hrd.getDictFromPrefix("key.read").iteritems():
        #     j.sal.fs.writeFile(filename=stor+"_read", contents=key)
        # for stor, key in serviceObj.hrd.getDictFromPrefix("key.write").iteritems():
        #     j.sal.fs.writeFile(filename=stor+"_write", contents=key)
