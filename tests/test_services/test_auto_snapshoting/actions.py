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
    RESULT_OK = 'OK'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s'
    failures = []
    import requests, sys, time
    service = job.service
    snapshots_total_number = 5


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

        autosnapshotting = service.producers['autosnapshotting'][0]

        snapshotInterval_value = autosnapshotting.model.data.snapshotInterval
        snapshotInterval = int(snapshotInterval_value[:snapshotInterval_value.find('m')])

        cleanupInterval_value = autosnapshotting.model.data.cleanupInterval
        cleanupInterval = int(cleanupInterval_value[:cleanupInterval_value.find('m')])

        time.sleep(snapshotInterval * snapshots_total_number)
        response = session.post(url=API_URL, data=API_BODY)

        if response.status_code == 200:
            snapshots = response.json()
            if len(snapshots) < snapshots_total_number:
                response_data = {'status_code': response.status_code,
                                 'content': response.content,
                                 'url': response.url,
                                 'machineId': machineId}
                failures.append('FAILED : %s %s' % ('test_auto_snapshoting', str(response_data)))

        else:
            response_data = {'status_code': response.status_code,
                             'content': response.content,
                             'url': response.url,
                             'machineId': machineId}
            failures.append('FAILED : %s %s' % ('test_auto_snapshoting', str(response_data)))

        time.sleep(cleanupInterval)
        response = session.post(url=API_URL, data=API_BODY)

        if response.status_code == 200:
            snapshots = response.json()
            if len(snapshots) > 1:
                response_data = {'status_code': response.status_code,
                                 'content': response.content,
                                 'url': response.url,
                                 'machineId': machineId}
                failures.append('FAILED : %s %s' % ('test_auto_snapshoting', str(response_data)))

        else:
            response_data = {'status_code': response.status_code,
                             'content': response.content,
                             'url': response.url,
                             'machineId': machineId}
            failures.append('FAILED : %s %s' % ('test_auto_snapshoting', str(response_data)))

        if failures:
            service.model.data.result = RESULT_FAILED % str(failures)
        else:
            service.model.data.result = RESULT_OK

    except:
        service.model.data.result = RESULT_ERROR % ('test_auto_snapshoting', str(sys.exc_info()[:2]))

    service.save()
