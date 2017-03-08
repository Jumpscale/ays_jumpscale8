def init_actions_(service, args):

    """

    this needs to returns an array of actions representing the depencies between actions.

    Looks at ACTION_DEPS in this module for an example of what is expected

    """
    # some default logic for simple actions
    return {

        'test_all': ['test_update_bp',
                     'test_create_bp', 'test_list_bps', 'test_delete_repo', 'test_get_repo',
                     'test_create_repo', 'test_list_repos', 'install']
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
    Tests create new repository api
    """
    import sys
    import os
    import requests
    import time
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    repos = []
    server_uri = model.data.uri
    server_uri = server_uri.strip('/')
    repo_name = 'testrepo_%s' %  time.time()
    fake_repo_url = 'https://githum.com/ahussin/%s.git' % repo_name
    try:
        service_uri = '/ays/repository'
        full_uri = '%s%s' % (server_uri, service_uri)
        # non-valid requests...no data sent
        res = requests.post(full_uri)
        if res.status_code != 400:
            failures.append('Wrong status code while creating new repository with invlid data. Expected [%s] found [%s]' % (400, res.status_code))
        # valid request
        data = {'name': repo_name, 'git_url': fake_repo_url}
        res = requests.post(full_uri, json=data)
        if res.status_code != 201:
            failures.append('Wrong status code while creating new repository. Expected [201] found [%s]' %  res.status_code)
        
        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        if repos:
            for repo in repos:
                repo.destroy()
        # delete the created repo
        full_uri = '%s/%s' % (full_uri, repo_name)
        requests.delete(full_uri)


def test_get_repo(job):
    """
    Tests get repository api
    """
    import sys
    import os
    import requests
    import time
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
        if res.status_code == 200:
            ays_repos = res.json()
            if len(ays_repos) > 0:
                repo_info = ays_repos[0]
                ays_repos = dict(zip([item['name'] for item in ays_repos], ays_repos))
                non_existing_repo = '%s_%s' % (repo_info['name'], time.time())
                while non_existing_repo in ays_repos:
                    non_existing_repo = non_existing_repo = '%s_%s' % (repo_info['name'], time.time())
                service_uri = '%s/%s' % (service_uri, repo_info['name'])
                full_uri = '%s%s' % (server_uri, service_uri)
                res = requests.get(full_uri)
                if  res.status_code != 200:
                    failures.append('Wrong status code while getting repository [%s] using uri [%s]' % (repo_info['name'], full_uri))
                # test non-existing repo
                service_uri = '%s/%s' % (service_uri, non_existing_repo)
                full_uri = '%s%s' % (server_uri, service_uri)
                res = requests.get(full_uri)
                if  res.status_code != 404:
                    failures.append('Wrong status code while getting non-existing repository [%s] using uri [%s]' % (repo_info['name'], full_uri))
        
        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        if repos:
            for repo in repos:
                repo.destroy()


def test_delete_repo(job):
    """
    Tests delete repository api
    """
    import sys
    import os
    import requests
    import time
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    repos = []
    server_uri = model.data.uri
    server_uri = server_uri.strip('/')
    repo_name = 'testrepo_%s' %  time.time()
    fake_repo_url = 'https://githum.com/ahussin/%s.git' % repo_name
    try:
        service_uri = '/ays/repository'
        full_uri = '%s%s' % (server_uri, service_uri)
        # list repos
        res = requests.get(full_uri)
        if res.status_code == 200:
            ays_repos = res.json()
            ays_repos = dict(zip([item['name'] for item in ays_repos], ays_repos))
            while repo_name in ays_repos:
                repo_name = 'testrepo_%s' %  time.time()
            # now create a repo with the non-existing name
            res = requests.post(full_uri, json={'name': repo_name, 'git_url': fake_repo_url})
            if res.status_code == 201:
                full_uri = '%s/%s' % (full_uri, repo_name)
                res = requests.delete(full_uri)
                if res.status_code != 204:
                    failures.append('Failed to delete repository. Error [%s]' % res.text)
            else:
                failures.append('Cannot test delete repository API. Cannot create test repo. Error [%s]' % res.text)
        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        if repos:
            for repo in repos:
                repo.destroy()


def test_list_bps(job):
    """
    Tests list blueprints API
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
        if res.status_code == 200:
            repo_info = res.json()
            if repo_info:
                repo_info = repo_info[0]                
                service_uri = '/ays/repository/%s/blueprint' % repo_info['name']
                full_uri = '%s%s' % (server_uri, service_uri)
                res = requests.get(full_uri)
                if res.status_code != 200:
                    failures.append('Failed to list blueprints using url [%s]. Error [%s]' % (full_uri, res.text))

        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        if repos:
            for repo in repos:
                repo.destroy()    


def test_create_bp(job):
    """
    Create test blueprint
    """
    import sys
    import os
    import requests
    import time
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    repos = []
    server_uri = model.data.uri
    server_uri = server_uri.strip('/')
    repo_info = None
    blueprint_name = None
    try:
        service_uri = '/ays/repository'
        full_uri = '%s%s' % (server_uri, service_uri)
        res = requests.get(full_uri)
        if res.status_code == 200:
            repo_info = res.json()
            if repo_info:
                repo_info = repo_info[0]                
                service_uri = '/ays/repository/%s/blueprint' % repo_info['name']
                full_uri = '%s%s' % (server_uri, service_uri)
                res = requests.get(full_uri)
                ays_bps = dict(zip([bp_info['name'] for bp_info in res.json()], res.json()))
                if res.status_code == 200:
                    blueprint_name = 'testbp_%s' % time.time()
                    while blueprint_name in ays_bps:
                        blueprint_name = 'testbp_%s' % time.time()
                    content = "test_recurring_actions__instance:\n\nactions:\n  - action: 'test'"
                    res = requests.post(full_uri, json={'name': blueprint_name, 'content': content})
                    if res.status_code != 201:
                        failures.append("Failed to create new blueprint. Error [%s]" % res.text)

        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        if repos:
            for repo in repos:
                repo.destroy()
        # delete the test blueprint
        if repo_info and blueprint_name:
            full_uri = '%s/ays/repository/%s/blueprint/%s' % (server_uri, repo_info['name'], blueprint_name)
            requests.delete(full_uri)



def test_update_bp(job):
    """
    Tests update blueprint API
    """
    import sys
    import os
    import requests
    import time
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    repos = []
    server_uri = model.data.uri
    server_uri = server_uri.strip('/')
    repo_info = None
    blueprint_name = None
    try:
        service_uri = '/ays/repository'
        full_uri = '%s%s' % (server_uri, service_uri)
        res = requests.get(full_uri)
        if res.status_code == 200:
            repo_info = res.json()
            if repo_info:
                repo_info = repo_info[0]                
                service_uri = '/ays/repository/%s/blueprint' % repo_info['name']
                full_uri = '%s%s' % (server_uri, service_uri)
                res = requests.get(full_uri)
                ays_bps = dict(zip([bp_info['name'] for bp_info in res.json()], res.json()))
                if res.status_code == 200:
                    blueprint_name = 'testbp_%s' % time.time()
                    while blueprint_name in ays_bps:
                        blueprint_name = 'testbp_%s' % time.time()
                    content = "test_recurring_actions__instance:\n\nactions:\n  - action: 'test'"
                    res = requests.post(full_uri, json={'name': blueprint_name, 'content': content})
                    if res.status_code == 201:
                        updated_content = "test_recurring_actions__instance2:\n\nactions:\n  - action: 'test'"
                        full_uri = '%s/ays/repository/%s/blueprint/%s' % (server_uri, repo_info['name'], blueprint_name)
                        res = requests.put(full_uri, json={'name': blueprint_name, 'content': content})
                        if res.status_code != 200:
                            failures.append('Failed to update blueprint using uri [%s]. Error[%s]' % (full_uri, res.text))
                            
        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        if repos:
            for repo in repos:
                repo.destroy()
        # delete the test blueprint
        if repo_info and blueprint_name:
            full_uri = '%s/ays/repository/%s/blueprint/%s' % (server_uri, repo_info['name'], blueprint_name)
            requests.delete(full_uri)