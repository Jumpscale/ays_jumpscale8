from JumpScale import j


class Actions(ActionsBaseMgmt):
    def install(self, service):
        cuisine = service.executor.cuisine
        cuisine.process.kill('dnsmasq')
        cuisine.package.install('dnsmasq')

        cmd = cuisine.bash.cmdGetPath('dnsmasq')

        main_ips = service.executor.cuisine.net.ips
        cuisine.ns.hostfile_set(service.parent.instance, main_ips[0])

        for node in service.producers.get('os'):
            cuisine.ns.hostfile_set(node.instance, node.executor.cuisine.net.ips[0])
            node.executor.cuisine.ns.nameservers = main_ips

        cuisine.processmanager.ensure('dnsmasq', '%s -d' % cmd)