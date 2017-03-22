def input(job):
    service = job.service
    data = job.service.model.data
    data.keyPath = j.sal.fs.joinPaths(service.path, 'id_rsa')
    j.sal.fs.createDir(service.path)

    if data.keyPriv is None or data.keyPriv == '':
        # generate key
        cmd = "ssh-keygen -q -t rsa -f {} -N '{}'".format(data.keyPath, data.keyPassphrase)
        rc, out, err = j.do.execute(cmd, showout=False)
        data.keyPriv = j.sal.fs.fileGetContents(data.keyPath)
        data.keyPub = j.sal.fs.fileGetContents(data.keyPath + '.pub')

    elif data.keyPriv is not None and data.keyPriv != '':
        # write keys into service directory
        j.sal.fs.writeFile(data.keyPath, data.keyPriv)
        j.sal.fs.writeFile(data.keyPath + '.pub', data.keyPub)

    j.sal.fs.chmod(data.keyPath, 0o600)
    j.sal.fs.chmod(data.keyPath + '.pub', 0o600)
