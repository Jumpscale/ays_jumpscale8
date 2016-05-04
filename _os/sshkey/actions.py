from JumpScale import j


class Actions():

    def getSSHKey(self):
        keydest = j.sal.fs.joinPaths(self.service.path, "sshkey_%s"%self.service.instance)
        privkey = j.sal.fs.fileGetContents(keydest)
        pubkey = j.sal.fs.fileGetContents(keydest + ".pub")
        return privkey, pubkey

    def _startAgent(self):
        # FIXME
        j.do.execute("ssh-agent", die=False, showout=False, outputStderr=False)

    def init(self):
        """
        create key
        """
        if self.service.hrd.get("key.name") == "":
            self.service.hrd.set("key.name", self.service.instance)

        name=self.service.hrd.get("key.name") 
        
        tmpdir=j.sal.fs.getTmpDirPath()

        if j.do.getSSHKeyPathFromAgent(name, die=False)!=None:
            keyfile = j.do.getSSHKeyPathFromAgent(name)
        elif '$(key.path)' != "":
            keyfile = '$(key.path)'
        else:
            keyfile=j.sal.fs.joinPaths(tmpdir,name)
            cmd = "ssh-keygen -t rsa -f %s -P '%s' " % (keyfile, self.service.hrd.getStr('key.passphrase'))
            print(cmd)
            j.sal.process.executeWithoutPipe(cmd)

        if not j.sal.fs.exists(keyfile):
            raise j.exceptions.Input("Cannot find ssh key location:%s"%keyfile)

        keydest = j.sal.fs.joinPaths(self.service.path, "sshkey_%s"%self.service.instance)
        j.sal.fs.copyFile(keyfile,keydest)
        j.sal.fs.copyFile(keyfile+".pub",keydest+".pub")

        privkey = j.sal.fs.fileGetContents(keydest)
        pubkey = j.sal.fs.fileGetContents(keydest + ".pub")

        self.service.hrd.set('key.pub', pubkey)
        self.service.hrd.set('key.priv', privkey)

        j.sal.fs.chmod(keydest, 0o600)
        j.sal.fs.chmod(keydest+".pub", 0o600)

        j.sal.fs.removeDir(tmpdir)

        self.install()


    def install(self):
        j.do.loadSSHAgent()
        self.start()


    def start(self):
        """
        Add key to SSH Agent if not already loaded
        """
        keypath=j.sal.fs.joinPaths(self.service.path, "sshkey_%s"%self.service.instance)
        j.do.loadSSHKeys(keypath)


    #not sure we can remove, key can be used for something else
    # def stop(self):
    #     """
    #     Remove key from SSH Agent
    #     """
    #     keyfile = self._getKeyPath()
    #     if j.do.getSSHKeyPathFromAgent('$(key.name)', die=False) is not None:
    #         keyloc = "/root/.ssh/%s" % '$(key.name)'
    #         cmd = 'ssh-add -d %s' % keyfile
    #         j.do.executeInteractive(cmd)



