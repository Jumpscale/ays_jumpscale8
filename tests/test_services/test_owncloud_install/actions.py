def init_actions_(service, args):
    """
    this needs to returns an array of actions representing the depencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """
    return {
        'test': ['install']
    }


def test(job):
    import time
    import sys

    try:
        service = job.service
        repo = service.aysrepo
        log = j.logger.get('test')
        log.addHandler(j.logger._LoggerFactory__fileRotateHandler('tests'))
        log.info('Test started')
        bocs = service.producers['blueowncloud'][0]
        fqdn = bocs.model.data.fqdn

        log.info('Check that tidb server is running on port 3306')
        tidbos = repo.servicesFind(actor='os.ssh.ubuntu', name='tidb')[0]
        out = tidbos.executor.cuisine.core.run("ps aux |  grep -o -F 'tidb-server -P 3306' -m 1")
        if out[1] != 'tidb-server -P 3306':
            service.model.data.result = 'FAILED : {} {}'.format('test_owncloud_install', str(sys.exc_info()[:2]))
            service.save()
            return


        log.info('Check if the owncloud site can respond back')
        ocos = repo.servicesFind(actor="os.ssh.ubuntu", name="owncloud")[0]
        ocos.executor.cuisine.core.run('echo "127.0.0.1 %s" >> /etc/hosts' % fqdn)
        out = ocos.executor.cuisine.core.run("curl %s -L | grep -o -F -m 1 'GreenITGlobe'" % fqdn)
        if out[1] != 'GreenITGlobe':
            service.model.data.result = 'FAILED : {} {}'.format('test_owncloud_install', str(sys.exc_info()[:2]))
            service.save()
            return
        service.model.data.result = 'OK : {} '.format('test_owncloud_install')

    except:
        service.model.data.result = 'ERROR : {} {}'.format('test_owncloud_install', str(sys.exc_info()[:2]))
    log.info('Test Ended')
    service.save()
