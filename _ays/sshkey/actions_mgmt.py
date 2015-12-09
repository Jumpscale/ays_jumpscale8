from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()



class Actions(ActionsBase):

    def _generateKey(self,serviceObj):
        keyfile=j.do.joinPaths(serviceObj.path,"key_$(key.name)")
        j.do.delete(keyfile)
        j.do.delete(keyfile+".pub")
        cmd="ssh-keygen -t rsa -f $(key.name) -P '$(key.passphrase)' -f '%s'"%keyfile
        j.sal.process.executeWithoutPipe(cmd)

        if not j.sal.fs.exists(path=keyfile):
            raise RuntimeError("cannot find path for key %s, was keygen well executed" % keyfile)

        privkey=j.do.readFile(keyfile)
        pubkey=j.do.readFile(keyfile+".pub")

        return privkey,pubkey

    def hrd(self, serviceObj):
        """
        create key
        """

        if '$(key.passphrase)'=="":
            print ("generate key")
            privkey,pubkey=self._generateKey(serviceObj)

            serviceObj.hrd.set("key.priv",privkey)
            serviceObj.hrd.set("key.pub",pubkey)

        try:
            keyloc=j.do.getSSHKeyFromAgent("$(key.name)",die=False)
        except:
            keyloc = None

        if keyloc==None:
            keyloc=j.do.joinPaths(serviceObj.path,"key_$(key.name)")

        j.do.chmod(keyloc, 0o600)

        keyfile=j.do.joinPaths(serviceObj.path,"key_$(key.name)")
        if not j.sal.fs.exists(path=keyfile):
            raise RuntimeError("could not find sshkey:%s"%keyfile)

        if j.do.getSSHKeyFromAgent("$(key.name)", die=False) is None:
            cmd = 'ssh-add %s' % keyfile
            j.do.executeInteractive(cmd)


    def install_post(self,serviceObj):
        self.start(serviceObj)
        return True

    def _getKeyPath(self,serviceObj):
        keyfile=j.do.joinPaths(serviceObj.path,"key_$(key.name)")
        if not j.sal.fs.exists(path=keyfile):
            raise RuntimeError("could not find sshkey:%s"%keyfile)
        return keyfile


    def start(self, serviceObj):
        """
        Add key to SSH Agent if not already loaded
        """
        keyfile=self._getKeyPath(serviceObj)
        if j.do.getSSHKeyFromAgent("$(key.name)", die=False) is None:
            cmd = 'ssh-add %s' % keyfile
            j.do.executeInteractive(cmd)

    def stop(self, serviceObj):
        """
        Remove key from SSH Agent
        """
        keyfile=self._getKeyPath(serviceObj)
        if j.do.getSSHKeyFromAgent('$(key.name)', die=False) is not None:
            keyloc = "/root/.ssh/%s" % '$(key.name)'
            cmd = 'ssh-add -d %s' % keyfile
            j.do.executeInteractive(cmd)

    def removedata(self, serviceObj):
        """
        remove key data
        """
        keyfile=self._getKeyPath(serviceObj)
        j.delete(keyfile)
        j.delete(keyfile+".pub")

        
