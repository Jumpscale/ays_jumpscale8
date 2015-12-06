from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        def askNodeInfo(node):
            nodeinfo = {}
            nodeinfo['name'] = j.tools.console.askString("Enter node name", node)
            nodeinfo['ip'] = j.tools.console.askString("Enter node IP")
            nodeinfo['client_port'] = j.tools.console.askInteger("Enter node client port", 7080)
            nodeinfo['messaging_port'] = j.tools.console.askInteger("Enter messaging port", 10000)
            nodeinfo['home'] = j.tools.console.askString("Enter node home dir", "/opt/arakoon/data/")
            return nodeinfo
        nodes = serviceObj.hrd.getList('cluster')
        for node in nodes:
            if len(serviceObj.hrd.getDictFromPrefix('master')) == 0:
                info = askNodeInfo(node)
                serviceObj.hrd.set('%s' % node, info)