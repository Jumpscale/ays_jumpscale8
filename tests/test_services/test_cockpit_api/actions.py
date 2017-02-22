def init_actions_(service, args):

    """

    this needs to returns an array of actions representing the depencies between actions.

    Looks at ACTION_DEPS in this module for an example of what is expected

    """
    # some default logic for simple actions
    return {

        'test_all': ['install', 'test_list_repos', 'test_create_repo']
    }

def test_all(job):
    """
    Test umbrella 
    """
    pass
    

def test_list_repos(job):
    """
    Tests list repositories API
    """
    import sys
    import os
    import requests
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    repos = []
    server_uri = model.data.uri
    server_uri = server_uri.strip('/')
    try:
        service_uri = '/ays/repository'
        full_uri = '%s%s' % (server_uri, service_uri)
        res = requests.get(full_uri)
        if res.status_code != 200:
            failures.append('Wrong response while testing [%s] service using uri [%s]. Error [%s]' % (service_uri, server_uri, res.text))
        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        if repos:
            for repo in repos:
                repo.destroy()

def test_create_repo(job):
    """
    Tests creaate new repository api
    """
    import sys
    import os
    import requests
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    repos = []
    server_uri = model.data.uri
    server_uri = server_uri.strip('/')
    try:
        service_uri = '/ays/repository'
        full_uri = '%s%s' % (server_uri, service_uri)
        res = requests.post(full_uri)
        if res.status_code != 400:
            failures.append('Wrong status code while creating new repository with invlid data. Expected [%s] found [%s]' % (400, res.status_code))
        import ipdb; ipdb.set_trace()
        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        if repos:
            for repo in repos:
                repo.destroy()
