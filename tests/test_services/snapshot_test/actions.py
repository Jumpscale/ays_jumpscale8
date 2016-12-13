def init_actions_(service, args):
    """
    this needs to returns an array of actions representing the depencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """

    # some default logic for simple actions


    return {
        'test_snapshot': ['install']
    }


def test_snapshot(job):
    import requests, sys
    service = job.service
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

        machine = service.producers['node.ovc'][0]
        machineId = machine.model.data.machineID

        API_URL = url + '/cloudapi/machine/listSnapshots'
        API_BODY = {'machineId': machineId}

        response = session.get(url=API_URL, data=API_BODY)

        if response.status_code == 200:
            service.model.data.result = 'OK : %s ' % 'test_snapshot'
        else:
            response_data = {'status_code': response.status_code,
                             'content': response.content}
            service.model.data.result = 'FAILED : %s %s' % ('test_snapshot',str(response_data))

    except:
        service.model.data.result = 'ERROR : %s %s' % ('test_snapshot', str(sys.exc_info()[:2]))
    service.save()


