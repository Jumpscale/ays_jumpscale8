from JumpScale import j

controller, name, new_disks, new_nics, memory, cpucount)

def install(job):
    service = job.service
    c = service.executor.cuisine
    controller = c.systemservices.kvm._controller
    name = service.model.dbobj.name
    disks = [disk.model() for disk in service.producers['disks']]

    nics = [disk.model.dbobj.name for disk in service.producers['bridges']]

    new_nics = list(map(lambda x: j.sal.kvm.Interface(controller, x,
                                                          j.sal.kvm.Network(controller, x, x, [])), nics))
    memory = service.model.dbobj.memory
    cpucount = service.model.dbobj.cpucount
    cloud_init = service.model.dbobj.cloud_init

    machine = j.sal.kvm.Machine(controller, name, disks, new_nics, memory, cpucount, cloud_init=cloud_init)