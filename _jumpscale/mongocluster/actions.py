from JumpScale import j

ActionsBase = service.aysrepo.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def install(self, service):
        nodes = service.getProducers('docker')
        cluster = {'shard': [], 'config': [], 'mongos': []}
        clusterconfig = service.hrd.get('clusterconfig')
        for node in nodes:
            print (node.instance)
            executor = node.action_methods_mgmt.getExecutor()
            nodeconfig = clusterconfig.get(node.instance, '')
            nodeconfig = {item.split(':')[0]: item.split(':')[1] for item in nodeconfig.split() if ':' in item}
            for role, port in nodeconfig.items():
                if role not in nodeconfig:
                    continue
                roleconfig = {'executor': executor}
                roleconfig['addr'] = executor.cuisine.hostname
                roleconfig['private_port'] = int(port)
                roleconfig['public_port'] = int(port)
                # TODO (*2*) path to db should be mounted
                roleconfig['dbdir'] = '/var/mongodbs/%s' % role
                cluster.get(role, []).append(roleconfig)

        cuisine = j.tools.cuisine.get()
        cuisine.apps.mongodb.mongoCluster(cluster['shard'], cluster['config'], cluster['mongos'])

    def load(self, service):
        nodes = service.getProducers('docker')
        cluster = {'shard': 'ourmongod', 'config': 'ourmongod_cfg', 'mongos': 'ourmongos'}
        clusterconfig = service.hrd.get('clusterconfig')
        for node in nodes:
            executor = node.action_methods_mgmt.getExecutor()
            nodeconfig = clusterconfig.get(node.instance, '')
            nodeconfig = [item.split(':')[0] for item in nodeconfig.split() if ':' in item]
            for role in nodeconfig:
                if role not in nodeconfig:
                    continue
                executor.cuisine.processmanager.start(cluster[role])
