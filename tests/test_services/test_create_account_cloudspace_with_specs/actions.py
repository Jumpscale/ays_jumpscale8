def init_actions_(service, args):
    """
    this needs to returns an array of actions representing the depencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """

    # some default logic for simple actions


    return {
        'test_create_account_cloudspace_with_specs': ['install']
    }


def test_create_account_cloudspace_with_specs(job):
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
        vdcs = service.producers['vdc']
        vdcIds = [x.model.data.cloudspaceID for x in vdcs]

        API_URL = url + '/restmachine/cloudapi/cloudspaces/get'

        for vdcId in vdcIds:
            API_BODY = {'cloudspaceId': vdcId}
            response = session.post(url=API_URL, data=API_BODY)
            if response.status_code != 200:
                response_data = {'status_code': response.status_code, 'content': response.content}
                service.model.data.result = 'FAILED : %s %s' % ('test_create_account_cloudspace_with_specs',response_data)
                break
        else:
            service.model.data.result = 'OK : %s ' % 'test_create_account_cloudspace_with_specs'
    except:
        service.model.data.result = 'ERROR : %s %s' % ('test_create_account_cloudspace_with_specs', str(sys.exc_info()[:2]))
    service.save()
