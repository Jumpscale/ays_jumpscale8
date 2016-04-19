from JumpScale import j


class Actions():

    #@todo should use cuisine methods
    def _generateKey(self):
        name = "key_%s" % self.service.hrd.getStr('key.name')
        keyfile = j.sal.fs.joinPaths(self.service.path, name)
        j.sal.fs.delete(keyfile)
        j.sal.fs.delete(keyfile + ".pub")
        cmd = "ssh-keygen -t rsa -f %s -P '%s' " % (keyfile, self.service.hrd.getStr('key.passphrase'))
        print(cmd)
        j.sal.process.executeWithoutPipe(cmd)

        if not j.sal.fs.exists(path=keyfile):
            raise j.exceptions.RuntimeError("cannot find path for key %s, was keygen well executed" % keyfile)

        privkey = j.sal.fs.fileGetContents(keyfile)
        pubkey = j.sal.fs.fileGetContents(keyfile + ".pub")

        return privkey, pubkey

    def _loadKey(self):
        name = "key_%s" % self.service.hrd.getStr('key.name')
        j.sal.fs.copyFile('$(key.path)', j.sal.fs.joinPaths(self.service.path, name))
        privkey = j.sal.fs.fileGetContents('$(key.path)')
        pubkey = j.sal.fs.fileGetContents('$(key.path)' + ".pub")

        return privkey, pubkey

    def _checkAgent(self):
        rc, out = j.do.execute("ssh-add -l", showout=False, outputStderr=False, die=False)

        # is running
        if rc == 0:
            return True

        # running but no keys
        if rc == 1:
            return True

        # another error
        return False

    def _startAgent(self):
        # FIXME
        j.do.execute("ssh-agent", die=False, showout=False, outputStderr=False)

    def init(self):
        """
        create key
        """
        if self.service.hrd.get("key.name") == "":
            self.service.hrd.set("key.name", self.service.instance)

        name = "key_%s" % self.service.hrd.getStr('key.name')

        if '$(key.path)' == "":
            privkey, pubkey = self._generateKey()
        else:
            privkey, pubkey = self._loadKey()

        self.service.hrd.set("key.priv", privkey)
        self.service.hrd.set("key.pub", pubkey)

        if self.service.hrd.get("agent.required") and not self._checkAgent():
            # print("agent not started")
            # self._startAgent()
            raise j.exceptions.RuntimeError("ssh-agent is not running and you need it, please run: eval $(ssh-agent -s)")

        try:
            keyloc = j.do.getSSHKeyPathFromAgent(name, die=False)
        except:
            keyloc = None

        if keyloc is None:
            keyloc = j.sal.fs.joinPaths(self.service.path, name)

        j.sal.fs.chmod(keyloc, 0o600)

        keyfile = j.sal.fs.joinPaths(self.service.path, name)
        if not j.sal.fs.exists(path=keyfile):
            raise j.exceptions.RuntimeError("could not find sshkey:%s" % keyfile)

        if j.do.getSSHKeyPathFromAgent(name, die=False) is None:
            # TODO: if previous key has been loaded with same name, kick that one out first
            cmd = 'ssh-add %s' % keyfile
            j.do.executeInteractive(cmd)

    def install_post(self):
        self.start()
        return True

    def _getKeyPath(self):
        keyfile = j.sal.fs.joinPaths(self.service.path, "key_$(key.name)")
        if not j.sal.fs.exists(path=keyfile):
            raise j.exceptions.RuntimeError("could not find sshkey:%s" % keyfile)
        return keyfile

    def start(self):
        """
        Add key to SSH Agent if not already loaded
        """
        keyfile = self._getKeyPath()
        if j.do.getSSHKeyPathFromAgent("$(key.name)", die=False) is None:
            cmd = 'ssh-add %s' % keyfile
            j.do.executeInteractive(cmd)

    def stop(self):
        """
        Remove key from SSH Agent
        """
        keyfile = self._getKeyPath()
        if j.do.getSSHKeyPathFromAgent('$(key.name)', die=False) is not None:
            keyloc = "/root/.ssh/%s" % '$(key.name)'
            cmd = 'ssh-add -d %s' % keyfile
            j.do.executeInteractive(cmd)

    def removedata(self):
        """
        remove key data
        """
        keyfile = self._getKeyPath(self.service)
        j.sal.fs.delete(keyfile)
        j.sal.fs.delete(keyfile + ".pub")

    def _delete_key(self):
        name = "key_%s" % self.service.hrd.getStr('key.name')
        keyfile = j.do.joinPaths(self.service.path, name)
        keyfile = keyfile.replace("!", "\!")
        cmd = "ssh-add -d %s" % (keyfile)
        print(cmd)
        j.sal.process.executeWithoutPipe(cmd)

    def uninstall(self):
        self._delete_key()

