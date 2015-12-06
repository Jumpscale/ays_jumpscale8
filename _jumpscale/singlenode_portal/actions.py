from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def init(self, serviceObj, args):
        for k, v in args.items():
            _, content = j.tools.text.ask(v)
            args[k] = content

        data = {
            'param.disk': '1',
            'param.mem': '100',
            'param.passwd': '',
            'param.port': '9999',
            'param.unixsocket': '0',
            'param.ip': 'localhost',
        }
        j.atyourservice.new(name='redis', instance='system', args=data, parent=serviceObj.parent)

        j.atyourservice.new(name='web', parent=serviceObj.parent)

        data = {
            'tcp.addr': 'localhost',
            'tcp.port.service': '27017',
            'param.replicaset': '',
        }
        j.atyourservice.new(name='mongodb', args=data, parent=serviceObj.parent)

        data = {
            'tcp.addr': 'localhost',
            'param.influxdb.client.dbname': 'main',
            'param.influxdb.client.login': 'root',
            'param.influxdb.client.passwd': args['param.rootpasswd'],
            'tcp.port.service': '8086',
        }
        j.atyourservice.new(name='influxdb', args=data, parent=serviceObj.parent)

        data = {
            'param.osis.connection.influxdb': 'main',
            'param.osis.connection.mongodb': 'main',
            'param.osis.superadmin.passwd': args['param.rootpasswd'],
        }
        j.atyourservice.new(name='osis', args=data, parent=serviceObj.parent)

        j.atyourservice.new(name='influxdb_client', parent=serviceObj.parent)
        j.atyourservice.new(name='mongodb_client', parent=serviceObj.parent)
        j.atyourservice.new(name='osis_client', parent=serviceObj.parent)

        data = {
            'smtp.login': '',
            'smtp.passwd': '',
            'smtp.port': '25',
            'smtp.sender': 'info@jumpscale.com',
            'smtp.server': 'localhost',
        }
        j.atyourservice.new(name='mailclient', args=data, parent=serviceObj.parent)

        data = {
            'param.cfg.admingroups': 'admin,',
            'param.cfg.authentication.method': 'osis',
            'param.cfg.contentdirs': '',
            'param.cfg.defaultspace': 'home',
            'param.cfg.force_oauth_instance': '',
            'param.cfg.gitlab.connection': 'main',
            'param.cfg.ipaddr': 'localhost',
            'param.cfg.port': '82',
            'param.cfg.secret': args['param.rootpasswd'],
            'param.portal.name': 'main',
            'param.portal.rootpasswd': args['param.rootpasswd'],
        }
        j.atyourservice.new(name='portal', args=data, parent=serviceObj.parent)
        j.atyourservice.new(name='portal_client', parent=serviceObj.parent)