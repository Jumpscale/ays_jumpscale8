import pytoml

from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):
    def build(self, service_obj):
        j.sal.ubuntu.install('mercurial')

        package = 'github.com/Jumpscale/agent2'

        syncthing = '/opt/build/git.aydo.com/binary/syncthing/syncthing/syncthing'

        # build package
        go = j.atyourservice.getService(name='go', parent=None)
        go.actions.buildProjectGodep(go, package='https://%s' % package)

        # path to bin and config
        gopath = go.hrd.getStr('gopath')
        bin_path = j.sal.fs.joinPaths(gopath, 'bin', 'agent2')
        cfg_path = j.sal.fs.joinPaths(gopath, 'src', package, 'agent.toml')
        ext_path = j.sal.fs.joinPaths(gopath, 'src', package, 'extensions')
        ext_conf_path = j.sal.fs.joinPaths(gopath, 'src', package, 'conf')

        # move bin to the binary repo
        j.do.pullGitRepo('https://git.aydo.com/binary/agent2.git')
        bin_repo = '/opt/code/git/binary/agent2/'
        for f in j.sal.fs.listFilesAndDirsInDir(bin_repo):
            if f.endswith('/.git'):
                continue
            j.sal.fs.removeDirTree(f)

        j.sal.fs.copyFile(bin_path, bin_repo)
        j.sal.fs.copyFile(cfg_path, j.sal.fs.joinPaths(bin_repo, 'agent2.toml'))
        j.sal.fs.copyDirTree(ext_path, j.sal.fs.joinPaths(bin_repo, 'extensions'))
        j.sal.fs.copyDirTree(ext_conf_path, j.sal.fs.joinPaths(bin_repo, 'conf'))

        # bundle syncthing.
        j.sal.fs.createDir(j.sal.fs.joinPaths(bin_repo, 'extensions', 'syncthing'))
        j.sal.fs.copyFile(syncthing, j.sal.fs.joinPaths(bin_repo, 'extensions', 'syncthing'))

        # upload bin to gitlab
        j.do.pushGitRepos(
            message='agent2 new build',
            name='agent2',
            account='binary'
        )

    def init(self, service_obj, args):
        ActionsBase.init(self, service_obj, args)

        depkey = "agentcontroller2"

        if depkey in service_obj._producers:
            res = service_obj._producers[depkey]
        else:
            # we need to check if there is a specific consumption specified, if not check generic one
            res = j.atyourservice.findServices(role=depkey)

        if len(res) == 0:
            # not deployed yet
            j.events.inputerror_critical(
                "Could not find dependency, please install.\nI am %s, I am trying to depend on %s" %
                (service_obj, depkey))
        elif len(res) > 1:
            j.events.inputerror_critical(
                "Found more than 1 dependent ays, please specify, cannot fullfil dependency requirement.\n" +
                "I am %s, I am trying to depend on %s" % (service_obj, depkey))
        else:
            ac = res[0]

        service_obj.consume(ac)

        ac_host, _, port = ac.hrd.getStr("param.webservice.host").partition(':')
        if not ac_host:
            if ac.parent and ac.parent.role == 'node':
                ac_host = ac.parent.hrd.getStr('node.tcp.addr')
            else:
                ac_host = 'localhost'

        args['agentcontroller2.url'] = 'http://%s:%s' % (ac_host, port)

        depkey = 'cfssl'
        if depkey in service_obj._producers:
            args['agentcontroller2.url'] = 'https://%s:%s' % (ac_host, port)
            cfssl_service = service_obj._producers[depkey][0]
            tls = j.tools.tls.get(cfssl_service.hrd.get('tls.dir'))
            subjects = [{
                "C": "AE",
                "L": "Dubai",
                "O": "GreenITGlobe",
                "OU": "0-complexity",
                "ST": "Dubai",
                "CN": "agent2-%s" % service_obj.instance
            }]
            hosts = ['localhost', ac_host]
            ca = cfssl_service.hrd.get('ca.cert')
            ca_key = cfssl_service.hrd.get('ca.key')
            cert, key = tls.createSignedCertificate('angent2-%s' % service_obj.instance, subjects, hosts, ca, ca_key)

            args['tls.cert'] = j.sal.fs.fileGetContents(cert)
            args['tls.key'] = j.sal.fs.fileGetContents(key)
            args['tls.ca'] = j.sal.fs.fileGetContents(ca)

    def _addExtraConfig(self, service_obj):
        cfg_path = j.sal.fs.joinPaths(j.dirs.baseDir, 'apps', 'agent2', 'conf')
        """
        [extensions.monitor]
        binary = "python2.7"
        cwd = "./extensions/jumpscript"
        args = ["wrapper.py", "jumpscript", "ays_monitor"]
            [extensions.jumpscript.env]
            AGENT_CONTROLLER_NAME = "main"
            SOCKET = "/tmp/jumpscript.sock"
            PYTHONPATH = "../"
        """
        ext = {
            'monitor': {
                'binary': 'python2.7',
                'cwd': './extensions/jumpscript',
                'args': ["wrapper.py", "jumpscale", "ays_monitor"],
                'env': {
                    'AGENT_CONTROLLER_NAME': 'main',
                    'SOCKET': '/tmp/jumpscript.sock',
                    'PYTHONPATH': '../'
                }
            }
        }

        with open(j.sal.fs.joinPaths(cfg_path, 'extensions.toml'), 'w') as toml:
            pytoml.dump(toml, {'extensions': ext})

    def configure(self, service_obj):
        import pytoml
        # agentcontroller = service_obj.hrd.get('agentcontroller')
        cfg_path = j.sal.fs.joinPaths(j.dirs.baseDir, 'apps/agent2/agent2.toml')
        cfg = pytoml.load(open(cfg_path))
        cfg['controllers']['main']['url'] = service_obj.hrd.getStr('agentcontroller2.url')
        cfg['main']['gid'] = int('$(gid)')
        cfg['main']['nid'] = int('$(nid)')
        cfg['main']['roles'] = service_obj.hrd.getList('roles')

        if len(service_obj.hrd.getDictFromPrefix('tls')) > 0:
            tls_path = j.sal.fs.joinPaths(service_obj.path, 'tls')
            j.sal.fs.createDir(tls_path)

            ca = j.sal.fs.joinPaths(tls_path, 'ca.pem')
            cert = j.sal.fs.joinPaths(tls_path, 'cert.pem')
            key = j.sal.fs.joinPaths(tls_path, 'key.pem')
            j.sal.fs.writeFile(filename=ca, contents=service_obj.hrd.getStr('tls.ca'))
            j.sal.fs.writeFile(filename=key, contents=service_obj.hrd.getStr('tls.key'))
            j.sal.fs.writeFile(filename=cert, contents=service_obj.hrd.getStr('tls.cert'))

            cfg['controllers']['main']['security'] = {'client_certificate': cert,
                                                      'client_certificate_key': key,
                                                      'certificate_authority': ca}

        pytoml.dump(open(cfg_path, 'w'), cfg)
        self._addExtraConfig(service_obj)
