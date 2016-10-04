# fake example


def input(job):
    return job.model.args


def init(job):
    print("INIT OF DATACENTER")
    return True


def install(job):
    '''
    #@todo
    '''
    raise RuntimeError('stop')
    return True


def start(job):
    return True


def stop(job):
    '''
    @todo stop all docker instances
    '''


def monitor(job):
    '''
    @todo monitor that docker is properly working
    '''

def processChange(job):
    print('process change here %s' % job.service)
    print('args: %s' % job.model.args)
