from JumpScale import j




ActionsBase = j.atyourservice.getActionsBaseClassNode()


class Actions(ActionsBase):


    def configure(self, serviceObj):

        j.sal.ubuntu.install("rsync")
        j.do.createDir("$(root)")

        for i1 in "1234567890abcdef":
            for i2 in "1234567890abcdef":
                j.do.createDir("$(root)/%s/%s"%(i1,i2))

        j.tools.cuisine.local.group_ensure("readgroup")

        homedirWrite = "/home/$(write.login)"
        j.tools.cuisine.local.user_ensure(name="$(write.login)", passwd=j.tools.idgenerator.generateGUID(), \
            home=homedirWrite, uid=None, gid=None, shell='/bin/bash', fullname=None, encrypted_passwd=True,group="readgroup")

        #@todo (*3*) look for all j.system.unix statements & change to j.tools.cuisine.local (no need to change deployed services)


        writeKeyPath = "/home/$(write.login)/.ssh/id_rsa"
        writeKeyPubPath = writeKeyPath+".pub"
        autorizedKeyPath = j.sal.fs.joinPaths(homedirWrite, ".ssh", "authorized_keys")


        j.sal.fs.createDir(j.sal.fs.getParent(writeKeyPath))
        j.sal.ubuntu.sshkeys_generate(path=writeKeyPath)
        if not j.sal.fs.exists(path=autorizedKeyPath):
            j.sal.fs.createEmptyFile(autorizedKeyPath)
        j.sal.fs.writeFile(filename=autorizedKeyPath, contents=j.sal.fs.fileGetContents(writeKeyPubPath)+'\n', append=True)

        #if not j.system.unix.unixUserExists("$(read.login)"):
        homedirRead = "/home/$(read.login)"
        j.tools.cuisine.local.user_ensure(name="$(read.login)", passwd=j.tools.idgenerator.generateGUID(), home=homedirRead, uid=None, gid=None, shell='/bin/bash', fullname=None, encrypted_passwd=True)

        readKeyPath = "/home/$(write.login)/.ssh/id_rsa"
        readKeyPubPath = readKeyPath+".pub"
        autorizedKeyPath = j.sal.fs.joinPaths(homedirWrite, ".ssh", "authorized_keys")

        j.sal.fs.createDir(j.sal.fs.getParent(readKeyPath))
        j.sal.ubuntu.sshkeys_generate(path=readKeyPath)
        if not j.sal.fs.exists(path=autorizedKeyPath):
            j.sal.fs.createEmptyFile(autorizedKeyPath)
        j.sal.fs.writeFile(filename=autorizedKeyPath, contents=j.sal.fs.fileGetContents(writeKeyPubPath)+'\n', append=True)

        j.sal.fs.chmod("$(root)", 0o760)
        j.sal.fs.chown("$(root)","$(write.login)","readgroup")



        readKey = j.sal.fs.fileGetContents(readKeyPath)
        writeKey = j.sal.fs.fileGetContents(writeKeyPath)
        serviceObj.hrd.set("read.key", readKey)
        serviceObj.hrd.set("write.key", writeKey)

        return True

    def sync(self, serviceObj):

        peers = []
        for item in serviceObj.hrd.prefix("peer"):
            item = item.replace("peer.", "")
            name = item.split(".", 1)[0]
            if name not in peers:
                peers.append(name)

        for peer in peers:
            root = serviceObj.hrd.get("peer.%s.root" % peer)
            login = serviceObj.hrd.get("peer.%s.read.login" % peer)
            passwd = serviceObj.hrd.get("peer.%s.read.passwd" % peer)
            addr = serviceObj.hrd.get("peer.%s.tcp.addr" % peer)

        print(peers)








