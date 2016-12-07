from JumpScale import j


def install(job):
    '''
    make sure docker is properly installed (use cuisine functionality)
    '''
    service = job.service
    cuisine = service.executor.cuisine
    if not cuisine.systemservices.docker.isInstalled():
        cuisine.systemservices.docker.install()


def start(job):
    pass


def stop(job):
    '''
    @todo stop all docker instances
    '''
    pass


def monitor(job):
    '''
    @todo monitor that docker is properly working
    '''
    pass
