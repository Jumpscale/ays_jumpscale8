from JumpScale import j


def install(job):

    service = job.service
    c = service.executor.cuisine
    url = service.model.dbobj.url

    c.systemservices.kvm.download_image(url)


def path(job):
    service = job.service
    c = service.executor.cuisine
    controller = c.systemservices.kvm._controller
    url = service.model.dbobj.url
    name = url.split('/')[-1]

    return j.sal.fs.joinPaths(controller, 'images', name)
