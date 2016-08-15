from JumpScale import j

class Actions(ActionsBaseMgmt):
    def _findWeavePeer(self, service):
        ips = list()
        services = service.aysrepo.findServices(role='os')
        for candidate in services:
            if not candidate.parent == service.parent and not candidate.parent.hrd.exists('publicip') or not candidate.hrd.getBool('weave', False):
                continue
            ip = candidate.parent.hrd.getStr('publicip')
            if ip:
                ips.append(ip)
        return ' '.join(ips) or None

    def install(self, service):
        machine = service.parent.actions.getMachine(service.parent)
        pf_existing = {'tcp': [], 'udp': []}
        for pf in machine.portforwardings:
            pf_existing[pf['protocol']].append(pf['publicPort'])
        print(pf_existing)

        if '6783' not in pf_existing['tcp']:
            machine.create_portforwarding('6783', '6783', 'tcp')
        if '6783' not in pf_existing['udp']:
            machine.create_portforwarding('6783', '6783', 'udp')
        if '6784' not in pf_existing['udp']:
            machine.create_portforwarding('6784', '6784', 'udp')

        for candidate in service.parent.children:  # ugly! make better
            if candidate.role == 'os':
                break
        candidate.executor.cuisine.apps.weave.build(peer=self._findWeavePeer(service))
