from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()



class Actions(ActionsBase):

    def _generateKeys(self,keyname,passphrase):
        keyloc = "/root/.ssh/%s" % keyname
        if j.sal.fs.exists(path=keyloc):
            return keyloc
            # raise RuntimeError("private key does already exist")

        if passphrase.strip() != "":
            j.sal.process.executeWithoutPipe("ssh-keygen -t rsa -f %s -P '%s' " % (keyloc,passphrase))
        else:
            j.sal.process.executeWithoutPipe("ssh-keygen -t rsa -f %s -P '' " % (keyloc))

        if not j.sal.fs.exists(path=keyloc):
            raise RuntimeError("cannot find path for key %s, was keygen well executed" % keyloc)

    def init(self, serviceObj,args):
        """
        create key
        """
        ActionsBase.init(self,serviceObj,args)

        passphrase = args.get('key.pass',"")

        # if 'key.name' not in args:
        #     args['key.name'] = ''
        ttype,args["key.name"] = j.tools.text.ask(args["key.name"])
        keyname=args["key.name"]

        if keyname.strip()=="":
            raise RuntimeError("keyname cannot be empty")
        try:
            keyloc=j.do.getSSHKeyFromAgent(keyname,die=False)
        except:
            keyloc = None

        if keyloc==None:
            self._generateKeys(keyname,passphrase=passphrase)
            keyloc = "/root/.ssh/%s" % keyname
            keynew=True
        else:
            keynew=False

        privkey=j.sal.fs.fileGetContents(keyloc)
        args["key.priv"]= privkey


        publoc = keyloc + ".pub"


        j.do.chmod(keyloc, 0o600)


        if not j.sal.fs.exists(path=publoc) or j.sal.fs.fileGetContents(publoc).strip()=="":
            if passphrase.strip()!="":
                cmd = "ssh-keygen -f %s -y -P '%s'> '%s'" % (keyloc, passphrase, publoc)
            else:
                cmd = "ssh-keygen -f %s -y > '%s'" % (keyloc, publoc)
            j.do.executeInteractive(cmd)
            j.do.chmod(publoc, 0o600)

        if j.sal.fs.fileGetContents(publoc).strip()=="":
            j.sal.fs.remove(publoc)
            raise RuntimeError("did not generate public key well, please do again.")

        pubkey = j.do.readFile(publoc)
        args["key.pub"]=pubkey

        if j.do.getSSHKeyFromAgent(keyname, die=False) is None:
            cmd = 'ssh-add %s' % keyloc
            j.do.executeInteractive(cmd)

        return True

    def start(self, serviceObj):
        """
        Add key to SSH Agent if not already loaded
        """
        if j.do.getSSHKeyFromAgent('$(key.name)', die=False) is None:
            keyloc = "/root/.ssh/%s" % '$(key.name)'
            cmd = 'ssh-add %s' % keyloc
            j.do.executeInteractive(cmd)

    def stop(self, serviceObj):
        """
        Remove key from SSH Agent
        """
        if j.do.getSSHKeyFromAgent('$(key.name)', die=False) is not None:
            keyloc = "/root/.ssh/%s" % '$(key.name)'
            cmd = 'ssh-add -d %s' % keyloc
            j.do.executeInteractive(cmd)

    def removedata(self, serviceObj):
        """
        remove key data
        """
        pass
