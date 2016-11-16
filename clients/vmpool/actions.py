from JumpScale import j

def install(job):

    service = job.service
    c = service.executor.cuisine

    name = service.model.data.name

    c.systemservices.kvm.install()
    c.systemservices.kvm.poolCreate(name)
