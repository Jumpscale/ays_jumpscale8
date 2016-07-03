from JumpScale import j


class Actions(ActionsBaseMgmt):

    def getSSHKey(self, service):
        keydest = j.sal.fs.joinPaths(service.path, "sshkey_%s"%service.instance)
        privkey = j.sal.fs.fileGetContents(keydest)
        pubkey = j.sal.fs.fileGetContents(keydest + ".pub")
        return privkey, pubkey

    def _startAgent(self, service):
        # FIXME
        j.do.execute("ssh-agent", die=False, showout=False, outputStderr=False)

    def init(self, service):
        """
        create key
        """
        if service.hrd.get("key.name") == "":
            service.hrd.set("key.name", service.instance)

        name=service.hrd.get("key.name")

        tmpdir=j.sal.fs.getTmpDirPath()

        if j.do.getSSHKeyPathFromAgent(name, die=False)!=None:
            keyfile = j.do.getSSHKeyPathFromAgent(name)
        elif service.hrd.get("key.path") != "":
            keyfile = service.hrd.get("key.path")
        else:
            keyfile=j.sal.fs.joinPaths(tmpdir,name)
            cmd = "ssh-keygen -t rsa -f %s -P '%s' " % (keyfile, service.hrd.getStr('key.passphrase'))
            print(cmd)
            j.sal.process.executeWithoutPipe(cmd)

        if not j.sal.fs.exists(keyfile):
            raise j.exceptions.Input("Cannot find ssh key location:%s"%keyfile)

        keydest = j.sal.fs.joinPaths(service.path, "sshkey_%s"%service.instance)
        if not keyfile == keydest:
            service.hrd.set("key.path", keydest)
            j.sal.fs.copyFile(keyfile,keydest)
            j.sal.fs.copyFile(keyfile+".pub",keydest+".pub")

        privkey = j.sal.fs.fileGetContents(keydest)
        pubkey = j.sal.fs.fileGetContents(keydest + ".pub")

        service.hrd.set('key.pub', pubkey)
        service.hrd.set('key.priv', privkey)

        j.sal.fs.chmod(keydest, 0o600)
        j.sal.fs.chmod(keydest+".pub", 0o600)

        j.sal.fs.removeDirTree(tmpdir)

    def install(self, service):
        j.do.loadSSHAgent()
        ###### TEMPORARY WORKAROUND #####
        rc, _ = service.executor.cuisine.core.run('ssh-add', die=False)
        if rc:
            service.executor.cuisine.core.run("eval `ssh-agent -s`")
        #################################
        self.start(service=service)


    def start(self, service):
        """
        Add key to SSH Agent if not already loaded
        """
        keypath=j.sal.fs.joinPaths(service.path, "sshkey_%s"%service.instance)
        j.do.loadSSHKeys(keypath)


    #not sure we can remove, key can be used for something else
    # def stop(self, service):
    #     """
    #     Remove key from SSH Agent
    #     """
    #     keyfile = self._getKeyPath()
    #     if j.do.getSSHKeyPathFromAgent('$(key.name)', die=False) is not None:
    #         keyloc = "/root/.ssh/%s" % '$(key.name)'
    #         cmd = 'ssh-add -d %s' % keyfile
    #         j.do.executeInteractive(cmd)
