from JumpScale import j


def input(job):
    """
    create key, if it doesn't exist
    """

    # THIS ONE IS FIXED
    args = {}

    if 'key.path' in job.model.args and job.model.args['key.path'] is not None and job.model.args['key.path'] != '':
        path = job.model.args['key.path']
        if not j.sal.fs.exists(path, followlinks=True):
            raise j.exceptions.Input(message="Cannot find ssh key:%s for service:%s" %
                                     (path, job.service), level=1, source="", tags="", msgpub="")

        args['key.path'] = j.sal.fs.joinPaths(job.service.path, "id_rsa")
        j.sal.fs.createDir(job.service.path)
        j.sal.fs.copyFile(path, args['key.path'])
        j.sal.fs.copyFile(path + '.pub', args['key.path'] + '.pub')
        args["key.priv"] = j.sal.fs.fileGetContents(path)
        args["key.pub"] = j.sal.fs.fileGetContents(path + '.pub')

    if 'key.name' in job.model.args:
        path = j.do.getSSHKeyPathFromAgent(job.model.args['key.name'])
        if not j.sal.fs.exists(path, followlinks=True):
            raise j.exceptions.Input(message="Cannot find ssh key:%s for service:%s" %
                                     (path, job.service), level=1, source="", tags="", msgpub="")

        args["key.priv"] = j.sal.fs.fileGetContents(path)
        args["key.pub"] = j.sal.fs.fileGetContents(path + '.pub')
        args.pop('key.name')

    if 'key.priv' not in args or args['key.priv'].strip() == "":
        print("lets generate private key")
        args['key.path'] = j.sal.fs.joinPaths(job.service.path, "id_rsa")
        j.sal.fs.createDir(job.service.path)
        j.sal.fs.remove(args['key.path'])
        cmd = "ssh-keygen -q -t rsa -f %s -N ''" % (args['key.path'])
        rc, out = j.sal.process.execute(cmd, die=True, outputToStdout=False, ignoreErrorOutput=False)
        args["key.priv"] = j.sal.fs.fileGetContents(args['key.path'])
        args["key.pub"] = j.sal.fs.fileGetContents(args['key.path'] + '.pub')

    return args
