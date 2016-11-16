from JumpScale import j

def install(job):

    service = job.service
    c = service.executor.cuisine

    c.systemservices.openvswitch.install()

    name = service.model.data.name
    ip = service.model.data.ip
    netmask = service.model.data.netmask
    masquerading = service.model.data.masquerading
    ipconfig = service.model.data.ipconfig
    dhcp = service.model.data.dhcp

    # create bridge vms1
    c.systemservices.openvswitch.networkCreate(name, ovs=False, start=False)
    if ipconfig:
        # configure the network and the natting
        c.net.netconfig(name, ip, netmask, masquerading=masquerading)
        c.processmanager.start('systemd-networkd')
    if dhcp:
        # add a dhcp sercer to the bridge
        c.apps.dnsmasq.config(name)
        c.apps.dnsmasq.install()

def destroy(job):

    service = job.service
    c = service.executor.cuisine

    name = service.model.data.name

    j.sal.kvm.Network.get_by_name(c.systemservices.openvswitch._controller, name).destroy()

def start(job):

    service = job.service
    c = service.executor.cuisine

    name = service.model.data.name

    j.sal.kvm.Network.get_by_name(c.systemservices.openvswitch._controller, name).start()

def stop(job):

    service = job.service
    c = service.executor.cuisine

    name = service.model.data.name

    j.sal.kvm.Network.get_by_name(c.systemservices.openvswitch._controller, name).stop()
