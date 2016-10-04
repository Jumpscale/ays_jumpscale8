def getSSHKey(service):
    from JumpScale import j
    keydest = j.sal.fs.joinPaths(service.path, "sshkey_%s" % service.instance)
    privkey = j.sal.fs.fileGetContents(keydest)
    pubkey = j.sal.fs.fileGetContents(keydest + ".pub")
    return privkey, pubkey


def init(service):
    """
    create key
    """
    from JumpScale import j
    if service.hrd.get("key.name") == "":
        service.hrd.set("key.name", service.instance)

    name = service.hrd.get("key.name")

    tmpdir = j.sal.fs.getTmpDirPath()

    if not j.do.checkSSHAgentAvailable():
        j.do._loadSSHAgent()

    if j.do.getSSHKeyPathFromAgent(name, die=False) is not None:
        keyfile = j.do.getSSHKeyPathFromAgent(name)
    elif service.hrd.get("key.path") != "":
        keyfile = service.hrd.get("key.path")
    else:
        keyfile = j.sal.fs.joinPaths(tmpdir, name)
        cmd = "ssh-keygen -t rsa -f %s -P '%s' " % (keyfile, service.hrd.getStr('key.passphrase'))
        print(cmd)
        j.sal.process.executeWithoutPipe(cmd)

    if not j.sal.fs.exists(keyfile):
        raise j.exceptions.Input("Cannot find ssh key location:%s" % keyfile)

    keydest = j.sal.fs.joinPaths(service.path, "sshkey_%s" % service.instance)
    if not keyfile == keydest:
        service.hrd.set("key.path", keydest)
        j.sal.fs.copyFile(keyfile, keydest)
        j.sal.fs.copyFile(keyfile+".pub", keydest + ".pub")

    privkey = j.sal.fs.fileGetContents(keydest)
    pubkey = j.sal.fs.fileGetContents(keydest + ".pub")

    service.hrd.set('key.pub', pubkey)
    service.hrd.set('key.priv', privkey)

    j.sal.fs.chmod(keydest, 0o600)
    j.sal.fs.chmod(keydest+".pub", 0o600)

    j.sal.fs.removeDirTree(tmpdir)


def install(job):
    from JumpScale import j

    def start(job):
        """
        Add key to SSH Agent if not already loaded
        """
        from JumpScale import j
        keypath = j.sal.fs.joinPaths(job.path, "sshkey_%s" % job.instance)
        j.do.loadSSHKeys(keypath)
    j.do._loadSSHAgent()
    start(service=job)


def start(service):
    """
    Add key to SSH Agent if not already loaded
    """
    from JumpScale import j
    keypath = j.sal.fs.joinPaths(service.path, "sshkey_%s" % service.instance)
    j.do.loadSSHKeys(keypath)
