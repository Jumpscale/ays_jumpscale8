def install(job):
    cuisine = job.service.executor.cuisine
    # install kvm
    cuisine.systemservices.kvm.install()
    # start libvirt-bin
    job.service.executeActionJob('start', inprocess=True)

    job.service.model.actions['uninstall'].state = 'new'
    job.service.saveAll()


def start(job):
    cuisine = job.service.executor.cuisine
    if not cuisine.processmanager.exists('libvirt-bin'):
        raise j.exceptions.RuntimeError("libvirt-bin service doesn't exists. \
                                         it should have been created during installation of this service")

    cuisine.processmanager.start('libvirt-bin')

    job.service.model.actions['stop'].state = 'new'
    job.service.saveAll()

def stop(job):
    cuisine = job.service.executor.cuisine
    if not cuisine.processmanager.exists('libvirt-bin'):
        raise j.exceptions.RuntimeError("libvirt-bin service doesn't exists. \
                                         it should have been created during installation of this service")

    cuisine.processmanager.stop('libvirt-bin')

    job.service.model.actions['start'].state = 'new'
    job.service.saveAll()


def uninstall(job):
    cuisine = job.service.executor.cuisine
    cuisine.systemservices.kvm.uninstall()

    job.service.model.actions['install'].state = 'new'
    job.service.saveAll()
