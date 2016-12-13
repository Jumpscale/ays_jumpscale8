from JumpScale import j


def install(job):
    '''
    make sure docker is properly installed (use cuisine functionality)
    '''
    import time
    service = job.service
    cuisine = service.executor.cuisine
    if not cuisine.systemservices.docker.isInstalled():
        timeout = 500
        while timeout > 0:
            try:
                cuisine.systemservices.docker.install()
            except Exception as e:
                if 'Resource temporarily unavailable' not in str(e):
                    raise RuntimeError(e)
                time.sleep(5)
                timeout -= 500


    if not cuisine.systemservices.dockercompose.isInstalled():
        cuisine.systemservices.dockercompose.install()


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
