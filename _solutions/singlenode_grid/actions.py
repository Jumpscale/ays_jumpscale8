from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def init(self, serviceObj, args):
        for k, v in args.items():
            if j.core.types.string.checkString(v):
                _, content = j.tools.text.ask(v)
                args[k] = content

        deps = []
        data = {
            'param.rootpasswd': args['param.rootpasswd']
        }
        snp = j.atyourservice.new(name='singlenode_portal', args=data, parent=serviceObj.parent)
        deps.append(snp)

        agentcontroller = j.atyourservice.new(name='agentcontroller', parent=serviceObj.parent)
        deps.append(agentcontroller)
        ac_client = j.atyourservice.new(name='agentcontroller_client', parent=serviceObj.parent, consume=agentcontroller)

        data = {
            'grid.id': args['param.gid'],
            'grid.node.roles': 'node',
        }
        jsagent = j.atyourservice.new(name='jsagent', args=data, parent=serviceObj.parent)
        deps.append(jsagent)

        data = {
            'param.password': args['param.rootpasswd'],
        }
        grafana = j.atyourservice.new(name='grafana', args=data, parent=serviceObj.parent)
        deps.append(grafana)

        data = {
            'tcp.port.service': 5000,
        }
        osis_eve = j.atyourservice.new(name='osis_eve', args=data, parent=serviceObj.parent)
        deps.append(osis_eve)

        gridportal = j.atyourservice.new(name='gridportal', args=data, parent=serviceObj.parent)
        deps.append(gridportal)

        statds_master = j.atyourservice.new(name='statsd-master', args=data, parent=serviceObj.parent)
        deps.append(statds_master)
        statsd_collector = j.atyourservice.new(name='statsd-collector', args=data, parent=serviceObj.parent, consume=statds_master)
        deps.append(statsd_collector)

        grafana_client = j.atyourservice.new(name='grafana_client', args=data, parent=serviceObj.parent)
        deps.append(grafana_client)

        portal = j.atyourservice.getService(role='portal')
        grafana = j.atyourservice.getService(domain='jumpscale', role='grafana')
        grafanaport = grafana.hrd.get('tcp.port.service')
        grafanaurl = "http://localhost:%s" % (grafanaport)
        grafana = {'path': '/grafana', 'dest': grafanaurl}
        eveproxy = {'path': '/proxy/eve', 'dest': "http://localhost:5000"}
        portal.hrd.set('proxy.1', grafana)
        portal.hrd.set('proxy.2', eveproxy)

        for dep in deps:
            serviceObj.consume(dep)

    def configure(self, serviceObj):
        roles = j.application.config.getList('grid.node.roles')
        if 'master' not in roles:
            roles.append('master')
            j.application.config.set('grid.node.roles', roles)

        # reload system config / whoAmI
        j.application.loadConfig()
        # restart jsagent
        j.atyourservice.getService(domain='jumpscale', name='jsagent').restart()
