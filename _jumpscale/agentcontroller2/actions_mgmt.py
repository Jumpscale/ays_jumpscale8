import hashlib
from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def build(self, service_obj):
        package = 'github.com/Jumpscale/agentcontroller2'
        # build package
        go = j.atyourservice.getService(name='go', parent=None)
        go.actions.buildProjectGodep(go, package='https://%s' % package)

        # path to bin and config
        gopath = go.hrd.getStr('gopath')
        # @todo can't we change the binary to agentcontroller2
        bin_path = j.sal.fs.joinPaths(gopath, 'bin', 'agentcontroller2')
        cfg_path = j.sal.fs.joinPaths(gopath, 'src', package, 'agentcontroller.toml')
        handlers_path = j.sal.fs.joinPaths(gopath, 'src', package, 'extensions')

        # move bin to the binary repo
        bin_repo = '/opt/code/git/binary/agentcontroller2/agentcontroller2/'

        j.do.pullGitRepo('https://git.aydo.com/binary/agentcontroller2.git')
        for f in j.sal.fs.listFilesAndDirsInDir('/opt/code/git/binary/agentcontroller2'):
            if f.endswith('/.git'):
                continue
            j.sal.fs.removeDirTree(f)

        j.sal.fs.createDir(bin_repo)
        j.sal.fs.copyFile(bin_path, bin_repo)
        j.sal.fs.copyFile(
            cfg_path,
            j.sal.fs.joinPaths(bin_repo, 'agentcontroller2.toml')
        )
        j.sal.fs.copyDirTree(handlers_path, j.sal.fs.joinPaths(bin_repo, 'extensions'))

        # upload bin to gitlab
        j.do.pushGitRepos(
            message='agentcontroller2 new build',
            name='agentcontroller2',
            account='binary'
        )

    def init(self, service_obj, args):
        super(Actions, self).init(service_obj, args)

        depkey = 'redis'
        if depkey not in service_obj._producers:
            j.events.opserror_critical(msg="Cant't find any service with role %s." % depkey,
                                       category="agentcontroller2.init")

        redis = service_obj._producers[depkey][0]
        args['param.redis.host'] = redis.hrd.getStr('param.ip') + ':' + redis.hrd.getStr('param.port')
        args['param.redis.password'] = redis.hrd.getStr('param.passwd')

        depkey = 'cfssl'
        if depkey in service_obj._producers:
            cfssl_service = service_obj._producers[depkey][0]
            tls = j.tools.tls.get(cfssl_service.hrd.get('tls.dir'))
            subjects = [{
                "C": "AE",
                "L": "Dubai",
                "O": "GreenITGlobe",
                "OU": "0-complexity",
                "ST": "Dubai",
                "CN": "agentcontroller2-%s" % service_obj.instance
            }]

            hosts = ['localhost']
            if 'tcp.addr' in args:
                hosts.append(args['tcp.addr'])
            ca = cfssl_service.hrd.get('ca.cert')
            ca_key = cfssl_service.hrd.get('ca.key')
            cert, key = tls.createSignedCertificate('ac2-%s' % service_obj.instance, subjects, hosts, ca, ca_key)

            args['tls.cert'] = j.sal.fs.fileGetContents(cert)
            args['tls.key'] = j.sal.fs.fileGetContents(key)
            args['tls.ca'] = j.sal.fs.fileGetContents(ca)

        depkey = 'influxdb'
        if depkey in service_obj._producers:
            influxdb_service = service_obj._producers[depkey][0]
            args['param.influxdb.host'] = influxdb_service.hrd.get('tcp.addr')
            args['param.influxdb.port'] = influxdb_service.hrd.get('tcp.port.service')
            args['param.influxdb.user'] = influxdb_service.hrd.get('admin.login')
            args['param.influxdb.password'] = influxdb_service.hrd.get('admin.password')
            args['param.influxdb.db'] = 'controller'

    def configure(self, service_obj):
        import pytoml
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the ays if anything needs to be started
        """

        # for backwards compatibility
        base = '/opt/jumpscale8/apps/agentcontroller2'

        toml = '/opt/jumpscale8/apps/agentcontroller2/agentcontroller2.toml'
        cfg = pytoml.load(open(toml))
        redis = service_obj.hrd.getStr('param.redis.host')
        cfg['main']['redis_host'] = redis
        cfg['main']['redis_password'] = service_obj.hrd.get('param.redis.password')

        # configure env var for events handlers
        redis_host, _, redis_port = redis.partition(':')
        cfg['events']['settings']['redis_address'] = redis_host
        cfg['events']['settings']['redis_port'] = redis_port
        cfg['events']['settings']['redis_password'] = service_obj.hrd.get('param.redis.password')

        influxdb = service_obj.hrd.getDictFromPrefix('param.influxdb')
        if influxdb:
            cfg['influxdb']['host'] = '%s:%s' % (influxdb['host'], influxdb['port'])
            cfg['influxdb']['db'] = influxdb['db']
            cfg['influxdb']['user'] = influxdb['user']
            cfg['influxdb']['password'] = influxdb['password']
            dbclient = j.clients.influxdb.get(host=influxdb['host'], port=influxdb['port'],
                                              username=influxdb['user'], password=influxdb['password'])
            if influxdb['db'] not in [db['name'] for db in dbclient.get_list_database()]:
                dbclient.create_database(influxdb['db'])

        syncthing = j.atyourservice.getService(name='syncthing')
        cfg['events']['settings']['syncthing_url'] = 'http://localhost:%s/' % syncthing.hrd.get('param.port')

        if len(service_obj.hrd.getDictFromPrefix('tls')) > 0:
            tls_path = j.sal.fs.joinPaths(service_obj.path, 'tls')
            j.sal.fs.createDir(tls_path)

            ca = j.sal.fs.joinPaths(tls_path, 'ca.pem')
            cert = j.sal.fs.joinPaths(tls_path, 'cert.pem')
            key = j.sal.fs.joinPaths(tls_path, 'key.pem')
            j.sal.fs.writeFile(filename=ca, contents=service_obj.hrd.getStr('tls.ca'))
            j.sal.fs.writeFile(filename=key, contents=service_obj.hrd.getStr('tls.key'))
            j.sal.fs.writeFile(filename=cert, contents=service_obj.hrd.getStr('tls.cert'))

            cfg['listen'][0]['tls'] = [{'cert': cert, 'key': key}]
            cfg['listen'][0]['clientCA'] = [{'cert': ca}]

        content = pytoml.dumps(cfg)
        j.sal.fs.writeFile(filename=toml, contents=content)

        # Start script syncing (syncthing)
        jumpscripts = j.sal.fs.joinPaths(base, 'jumpscripts')

        j.sal.fs.createDir(jumpscripts)

        syncthing_id = syncthing.actions.get_syncthing_id(syncthing)
        folderid = 'jumpscripts-%s' % hashlib.md5(syncthing_id).hexdigest()
        syncthing.actions.add_folder(syncthing, folderid, jumpscripts)
