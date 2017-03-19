def init_actions_(service, args):
    """
    this needs to returns an array of actions representing the depencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """

    # some default logic for simple actions


    return {
        'test_create_account': ['install']
    }


def test_create_account(job):
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

        account = service.producers['account'][0]
        accountId = account.model.data.accountID
        maxMemoryCapacity = account.model.data.maxMemoryCapacity
        maxCPUCapacity = account.model.data.maxCPUCapacity
        maxDiskCapacity = account.model.data.maxDiskCapacity
        maxNumPublicIP =  account.model.data.maxNumPublicIP
        accountUsers = account.model.data.accountusers

        API_URL = url + '/restmachine/cloudapi/accounts/get'
        API_BODY = {'accountId': accountId}

        response = session.post(url=API_URL, data=API_BODY)

        limits = response.json()['resourceLimits']
        actual_limits = [limits['CU_M'],limits['CU_D'], limits['CU_I'], limits['CU_C']]
        expected_limits = [maxMemoryCapacity, maxDiskCapacity, maxNumPublicIP, maxCPUCapacity]

        accountUsers_ = [u['userGroupId'] for u in response.json()['acl']]

        if response.status_code == 200 and actual_limits == expected_limits and set(accountUsers) == set(accountUsers_):
            service.model.data.result = 'OK : %s ' % 'test_create_account'
        else:
            response_data = {'status_code': response.status_code,
                             'content': response.content}
            service.model.data.result = 'FAILED : %s %s' % ('test_create_account',response_data)

    except:
        service.model.data.result = 'ERROR : %s %s' % ('test_create_account', str(sys.exc_info()[:2]))
    service.save()
