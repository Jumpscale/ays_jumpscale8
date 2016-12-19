def init_actions_(service, args):
    """
    this needs to returns an array of actions representing the depencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """

    # some default logic for simple actions


    return {
        'test_auto_snapshoting': ['install']
    }


def test_auto_snapshoting(job):
    import requests, sys, time
    service = job.service
    #import ipdb; ipdb.set_trace()
    try:
        g8client = service.producers['g8client'][0]
        url = 'https://' + g8client.model.data.url
        username = g8client.model.data.login
        password = g8client.model.data.password

        login_url = url + '/restmachine/system/usermanager/authenticate'
        credential = {'name': username,
                      'secret': password}
        session = requests.Session()
        session.post(url=login_url, data=credential)

        machine = service.producers['node'][0]
        machineId = machine.model.data.machineId

        API_URL = url + '/restmachine/cloudapi/machines/listSnapshots'
        API_BODY = {'machineId': machineId}

        time.sleep(360)
        response = session.post(url=API_URL, data=API_BODY)

        if response.status_code == 200:
            snapshots = response.json()
            if len(snapshots) > 0:
                service.model.data.result = 'OK : %s ' % 'test_auto_snapshoting'
            else:
                response_data = {'status_code': response.status_code,
                                 'content': response.content,
                                 'url': response.url,
                                 'machineId': machineId}
                service.model.data.result = 'FAILED : %s %s' % ('test_auto_snapshoting', str(response_data))

        else:
            response_data = {'status_code': response.status_code,
                             'content': response.content,
                             'url': response.url,
                             'machineId': machineId}
            service.model.data.result = 'FAILED : %s %s' % ('test_auto_snapshoting', str(response_data))

    except:
        service.model.data.result = 'ERROR : %s %s' % ('test_auto_snapshoting', str(sys.exc_info()[:2]))
    service.save()
