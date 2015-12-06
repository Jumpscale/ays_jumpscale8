from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def init(self, serviceObj, args):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """
        super(Actions, self).init(serviceObj, args)

        for key, arg in args.items():
            if j.core.types.string.check(arg) and arg.startswith('@ASK'):
                _, args[key] = j.tools.text.ask(arg)

        nodes = args['nodes'] if 'nodes' in args else []
        settings = args['cfg']
        nodename = args['nodename']
        settingsdir = j.sal.fs.getDirName(settings)
        j.sal.fs.createDir(settingsdir)

        def askNodeInfo():
            print("describe a node:")
            nodeinfo = {}
            nodeinfo['name'] = j.console.askString("Enter node name", "node1")
            nodeinfo['ip'] = j.console.askString("Enter node IP")
            nodeinfo['client_port'] = j.console.askInteger("Enter node client port", 7080)
            nodeinfo['messaging_port'] = j.console.askInteger("Enter messaging port", 10000)
            nodeinfo['home'] = j.console.askString("Enter node home dir", "/opt/arakoon/data/")
            return nodeinfo

        if not nodes:
            if 'clusterid' not in args:
                args['clusterid'] = j.console.askString('Enter cluster id', 'grid')
            while True:
                node = askNodeInfo()
                args['nodes.%s' % node['name']] = node
                nodes.append(node)
                if not j.console.askYesNo("Add another node"):
                    break

            args['nodes'] = ','.join([node['name'] for node in nodes])

    def configure(self, serviceObj):
        settings = serviceObj.hrd.getStr('cfg')
        settingsdir = j.sal.fs.getDirName(settings)
        j.sal.fs.createDir(settingsdir)

        clusterid = serviceObj.hrd.get('clusterid')
        nodename = serviceObj.hrd.get('nodename')
        xnodes = serviceObj.hrd.getList('nodes')
        nodes = []
        for node in xnodes:
            key = node.replace('"', '')
            data = serviceObj.hrd.get('nodes.' + key)
            nodes.append(data)
            if data['name'] == nodename:
                j.sal.fs.createDir(data['home'])

        j.sal.fs.remove(settings)
        config = j.tools.inifile.open(settings)
        config.addSection('global')
        config.addParam('global', 'cluster_id', clusterid)
        config.addParam('global', 'cluster', ', '. join(node['name'] for node in nodes))
        config.addSection('default_log_config')
        config.addParam('default_log_config', 'client_protocol', 'info')
        config.addParam('default_log_config', 'paxos', 'info')
        config.addParam('default_log_config', 'tcp_messaging', 'info')
        for node in nodes:
            config.addSection(node['name'])
            for key, value in node.items():
                if key == 'name':
                    continue
                config.addParam(node['name'], key, value)
            config.addParam(node['name'], 'log_dir', node['home'])
            config.addParam(node['name'], 'log_level', 'info')
            config.addParam(node['name'], 'log_config', 'default_log_config')
        config.write()

        if j.do.TYPE.lower().startswith("ubuntu64"):
            j.sal.ubuntu.downloadInstallDebPkg("https://git.aydo.com/binary/arakoon/raw/master/deb/arakoon_1.8.9_amd64.deb", minspeed=50)

        return True
