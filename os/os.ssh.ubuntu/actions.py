def install(job):
    from JumpScale import j
    service = job.service
    if 'sshkey' not in service.producers:
        raise j.exceptions.AYSNotFound("No sshkey service consumed. please consume an sshkey service")

    sshkey = service.producers['sshkey'][0]
    service.logger.info("authorize ssh key to machine")
    node = service.parent

    pf = {}
    for ports in node.model.data.ports:
        ss = ports.split(':')
        pf[int(ss[0])] = int(ss[1])

    # used the login/password information from the node to first connect to the node and then authorize the sshkey
    # for root user
    args = {
        "allow_agent": True,
        "look_for_keys": True,
        "timeout": 5,
        "usecache": False,
        "passphrase": None
    }

    args["port"] = pf[22] if len(pf) else 22
    args["addr"] = node.model.data.ipPublic if node.model.data.ipPublic else "localhost"
    args["login"] = node.model.data.sshLogin if node.model.data.sshLogin else "root"
    args["passwd"] = node.model.data.sshPassword if node.model.data.sshPassword else None

    executor = j.tools.executor.getSSHBased(**args)
    executor.cuisine.ssh.authorize("root", sshkey.model.data.keyPub)


def getExecutor(job):
    from JumpScale import j
    service = job.service
    if 'sshkey' not in service.producers:
        raise j.exceptions.AYSNotFound("No sshkey service consumed. please consume an sshkey service")

    sshkey = service.producers['sshkey'][0]
    node = service.parent
    key_path = j.sal.fs.joinPaths(sshkey.path, 'id_rsa')

    # here we need to check if the sshkey consumed by this service is loaded, if not we load it
    # and then we create the executor
    if not j.do.checkSSHAgentAvailable():
        j.do._loadSSHAgent()

    if key_path not in j.do.listSSHKeyFromAgent():
        j.do.loadSSHKeys(key_path)

    # search wich port expose ssh
    pf = {}
    for ports in node.model.data.ports:
        ss = ports.split(':')
        if len(ss) != 2:
            continue
        pf[int(ss[0])] = int(ss[1])

    executor = j.tools.executor.getSSHBased(addr=node.model.data.ipPublic, port=pf[22],
                                            login='root', passwd=None,
                                            allow_agent=True, look_for_keys=True, timeout=5, usecache=False,
                                            passphrase=None)
    return executor
