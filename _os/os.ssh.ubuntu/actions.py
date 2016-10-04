def init(job):
    if job.service.model.data.aysfs:
        job.aysrepo.new('aysfs', args={'os': job.instance}, parent=job)

    if job.service.model.data.weave:
        weave = job.aysrepo.new('weave', instance=job.instance, parent=job.parent)
    # if agent:
    #     instantiate agent
    # sshkey = service.aysrepo.getService(role='sshkey', instance=service.hrd.getStr('sshkey'))
    # service.hrd.set("ssh.key.public", sshkey.hrd.get("key.pub"))
    # service.hrd.set("ssh.key.private", sshkey.hrd.get("key.priv"))

    # if service.hrd.get("system.backdoor.passwd").strip() == "":
    #     service.hrd.set("system.backdoor.passwd", j.data.idgenerator.generateXCharID(12))
    return True


def getExecutor(service):
    from JumpScale import j
    sshkey = service.producers['sshkey'][0]
    pubkey = sshkey.hrd.get('key.pub')
    executor = j.tools.executor.getSSHBased(service.hrd.get("ssh.addr"), service.hrd.getInt("ssh.port"), 'root')
    executor.authorizeKey(pubkey=pubkey)
    return executor


def monitor(service):
    from JumpScale import j
    sshkey = service.producers.get('sshkey')[0]
    ssh_path = sshkey.service.hrd.get('key.path')
    sshkey_passphrase = sshkey.service.hrd.get('key.passphrase')

    addr = None
    if service.parent.templatename == 'node.ovc':
        # OVC natting doesn't allow a node to connect to itself
        if service.hrd.exists('private.addr'):
            addr = service.hrd.get('private.addr')
        else:
            return True
    addr = addr or service.hrd.get("ssh.addr")
    j.sal.nettools.tcpPortConnectionTest(addr, service.hrd.getInt("ssh.port"), timeout=5)
    client = j.clients.ssh.get(service.hrd.get("ssh.addr"),
                               port=service.hrd.getInt("ssh.port"),
                               login='root',
                               passwd=None,
                               stdout=True,
                               forward_agent=False,
                               allow_agent=False,
                               look_for_keys=False,
                               key_filename=ssh_path,
                               passphrase=sshkey_passphrase,
                               timeout=5,
                               die=True)
    try:
        client.execute('hostname')  # just to make sure connection is valid
        return True
    except Exception as e:
        return False


def install(service):
    def getExecutor(service):
        from JumpScale import j
        sshkey = service.producers['sshkey'][0]
        pubkey = sshkey.hrd.get('key.pub')
        executor = j.tools.executor.getSSHBased(service.hrd.get("ssh.addr"), service.hrd.getInt("ssh.port"), 'root')
        executor.authorizeKey(pubkey=pubkey)
        return executor

    if 'sshkey' in service.producers:
        sshkey = service.producers['sshkey'][0]
        sshkey_pub = sshkey.hrd.get('key.pub')
    else:
        raise RuntimeError("No sshkey found. please consume an sshkey service")

    print("authorize ssh key to machine")

    executor = getExecutor(service)
    cuisine = executor.cuisine

    for ssh in service.hrd.getList('authorized_sshkeys', []):
        cuisine.ssh.authorize('root', ssh)

    cuisine.ssh.authorize('root', sshkey_pub)
