def install(job):
    service = job.service
    if 'sshkey' not in service.producers:
        raise j.exceptions.AYSNotFound("No sshkey service consumed. please consume an sshkey service")

    sshkey = service.producers['sshkey'][0]
    service.logger.info("authorize ssh key to machine")
    node = service.parent

    # Looking in the parents chain is needed when we have nested nodes (like a docker node on top of an ovc node)
    # we need to find all the ports forwarding chain to reach the inner most node.
    ssh_port = '22'
    for parent in service.parents:
        if parent.model.role != 'node':
            continue
        for port in parent.model.data.ports:
            src, _, dst = port.partition(':')
            if ssh_port == dst:
                ssh_port = src
                break

    service.model.data.sshPort = int(ssh_port)

    sshkey = service.producers['sshkey'][0]
    key_path = j.sal.fs.joinPaths(sshkey.path, 'id_rsa')
    if not j.sal.fs.exists(sshkey.path):
        # raise j.exceptions.RuntimeError("sshkey path not found at %s" % key_path)
        key_path = None
    password = node.model.data.sshPassword if node.model.data.sshPassword != '' else None

    # used the login/password information from the node to first connect to the node and then authorize the sshkey for root
    executor = j.tools.executor.getSSHBased(addr=node.model.data.ipPublic, port=service.model.data.sshPort,
                                            login=node.model.data.sshLogin, passwd=password,
                                            allow_agent=True, look_for_keys=True, timeout=5, usecache=False,
                                            passphrase=None, key_filename=key_path)
    executor.cuisine.ssh.authorize("root", sshkey.model.data.keyPub)
    service.saveAll()


def getExecutor(job):
    service = job.service
    if 'sshkey' not in service.producers:
        raise j.exceptions.AYSNotFound("No sshkey service consumed. please consume an sshkey service")

    sshkey = service.producers['sshkey'][0]
    node = service.parent
    key_path = j.sal.fs.joinPaths(sshkey.path, 'id_rsa')

    executor = j.tools.executor.getSSHBased(addr=node.model.data.ipPublic, port=service.model.data.sshPort,
                                            login='root', passwd=None,
                                            allow_agent=True, look_for_keys=True, timeout=5, usecache=False,
                                            passphrase=None, key_filename=key_path)
    return executor
