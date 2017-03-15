def init_actions_(service, args):
    """
    this needs to returns an array of actions representing the depencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """
    return {
        'test': ['install']
    }


def test(job):
    import sys
    import time
    try:
        service = job.service
        repo = service.aysrepo
        log = j.logger.get('test')
        log.addHandler(j.logger._LoggerFactory__fileRotateHandler('tests'))
        log.info('Test started')

        log.info('check if there is influx process running')
        influxos = repo.servicesFind(actor='os.ssh.ubuntu', name = 'influxdb')[0]
        cuisine = influxos.executor.cuisine
        cuisine.apps.influxdb.start()
        check = cuisine.core.run('ps aux | grep influx | grep -v grep | wc -l')
        if int(check[1]) < 1:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_ays_build',
                                        'No process running fro influx',
                                        str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('check if there is mongo process running')
        mongoos = repo.servicesFind(actor='os.ssh.ubuntu', name = 'mongodb')[0]
        cuisine = mongoos.executor.cuisine
        cuisine.apps.mongodb.start()
        time.sleep(4)
        check = cuisine.core.run('/opt/jumpscale8/bin/mongo --host 127.0.01 --port 27017 --eval "print("1234")" | grep -o -F "1234"')
        if check[1] != '1234':
            service.model.data.result = 'FAILED : {} {} {}'.format('test_ays_build',
                                        'mongod is not responding back', str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('check if redis is running port 6379')
        redisos = repo.servicesFind(actor='os.ssh.ubuntu', name = 'redis')[0]
        cuisine = redisos.executor.cuisine
        cuisine.apps.redis.start()
        check = cuisine.core.run('/opt/jumpscale8/bin/redis-cli -h 127.0.0.1 -p 6379 -r 2 Ping')
        if check[1] != 'PONG\nPONG':
            service.model.data.result = 'FAILED : {} {} {}'.format('test_ays_build',
                                        'redis is not responding back', str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('check if grafana is running on port 3000')
        grafanaos = repo.servicesFind(actor='os.ssh.ubuntu', name = 'grafana')[0]
        cuisine = grafanaos.executor.cuisine
        cuisine.apps.grafana.start()
        check = cuisine.core.run('netstat -ntlp | grep grafana | grep -o -F "3000"')
        if check[1] != '3000':
            service.model.data.result = 'FAILED : {} {} {}'.format('test_ays_build',
                                        'grafana is not running on port 3000',
                                         str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('check if shellinabox package is installed')
        shellinaboxos = repo.servicesFind(actor='os.ssh.ubuntu', name = 'shellinabox')[0]
        cuisine = shellinaboxos.executor.cuisine
        check = cuisine.core.run('dpkg -l shellinabox | grep -o -F "shellinabox"')
        if check[1] != 'shellinabox':
            service.model.data.result = 'FAILED : {} {} {}'.format('test_ays_build',
                                        'shellinabox package not found', str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('check if pip3 and base packages are installed')
        pythonos = repo.servicesFind(actor='os.ssh.ubuntu', name = 'python')[0]
        cuisine = pythonos.executor.cuisine
        check = cuisine.core.run('dpkg -l  python3-pip | grep -o -F "python3-pip"')
        if check[1] != 'python3-pip':
            service.model.data.result = 'FAILED : {} {} {}'.format('test_ays_build',
                                        'python3-pip package not found', str(sys.exc_info()[:2]))
            service.save()
            return
        check = cuisine.core.run('dpkg -l  base | grep  -o -F "base"')
        if check[1] != 'base':
            service.model.data.result = 'FAILED : {} {} {}'.format('test_ays_build',
                                        'base package not found', str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('check if jumpscale installation went fine')
        jumpscaleos = repo.servicesFind(actor='os.ssh.ubuntu', name = 'jumpscale')[0]
        cuisine = jumpscaleos.executor.cuisine
        check = cuisine.core.run('js "print(1)"')
        if check[1] != '1':
            service.model.data.result = 'FAILED : {} {} {}'.format('test_ays_build',
                                        'Jumpscale installation is broken',
                                         str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('Check if there is a portal running process')
        portalos = repo.servicesFind(actor='os.ssh.ubuntu', name = 'portal')[0]
        cuisine = portalos.executor.cuisine
        cuisine.apps.portal.start()
        check = cuisine.core.run('ps aux | grep portal | grep -v grep | wc -l')
        if int(check[1]) < 1:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_ays_build',
                                        'No process running for portal',
                                         str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('check if cockpit is running')
        cockpitos = repo.servicesFind(actor='os.ssh.ubuntu', name = 'cockpit')[0]
        cuisine = cockpitos.executor.cuisine
        cuisine.solutions.cockpit.start()
        check = cuisine.core.run('ps aux | grep cockpit | grep -v grep | wc -l')
        if int(check[1]) < 1:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_ays_build',
                                        'No process running for cockpit',
                                         str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('check if godep binaries are there')
        golangos = repo.servicesFind(actor='os.ssh.ubuntu', name = 'golang')[0]
        cuisine = golangos.executor.cuisine
        check = cuisine.core.run('ls /optvar/go/bin/godep')
        if check[1] != '/optvar/go/bin/godep':
            service.model.data.result = 'FAILED : {} {} {}'.format('test_ays_build',
                                        'godep is not there', str(sys.exc_info()[:2]))
            service.save()
            return

        # issue in fs: https://github.com/Jumpscale/ays_build/issues/10
        log.info('check if fs is running')
        fsos = repo.servicesFind(actor='os.ssh.ubuntu', name = 'fs')[0]
        cuisine = fsos.executor.cuisine
        cuisine.systemservices.g8osfs.start()
        check = cuisine.core.run('sv status fs | grep -o -F "up:"')
        if check[1] !=  'up:':
            service.model.data.result = 'FAILED : {} {} {}'.format('test_ays_build',
                                        'No process running for fs',
                                         str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('check if geodns is running on port 5053')
        geodnsos = repo.servicesFind(actor='os.ssh.ubuntu', name = 'geodns')[0]
        cuisine = geodnsos.executor.cuisine
        cuisine.apps.geodns.start()
        check = cuisine.core.run('netstat -ntlp | grep geodns | grep -o -F 5053')
        if check[1] !=  '5053':
            service.model.data.result = 'FAILED : {} {} {}'.format('test_ays_build',
                                        'No process running for geodns or wrong port',
                                         str(sys.exc_info()[:2]))
            service.save()
            return

        # issue in tidb: https://github.com/Jumpscale/ays_build/issues/8
        # tidbos = repo.servicesFind(actor='os.ssh.ubuntu', name = 'tidb')[0]
        # we can add this check when the issue is fixed (scality can cover it)

        # issue in scality: https://github.com/Jumpscale/ays_build/issues/9
        log.info('check if there is scality process running ')
        scalityos = repo.servicesFind(actor='os.ssh.ubuntu', name = 'scality')[0]
        cuisine = owncloudos.executor.cuisine
        cuisine.apps.s3server.start()
        check = cuisine.core.run('ps aux | grep scalityS3 | grep -v grep | wc -l')
        if int(check[1]) < 1:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_ays_build',
                                        'No process running for scality',
                                         str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('check if owncloud is running fine')
        owncloudos = repo.servicesFind(actor='os.ssh.ubuntu', name = 'owncloud')[0]
        cuisine = owncloudos.executor.cuisine
        cuisine.apps.owncloud.start(sitename='jsowncloud.com')
        check = cuisine.core.run('ls /optvar/cfg/nginx/etc/sites-enabled/jsowncloud.com')
        if check[1] != '/optvar/cfg/nginx/etc/sites-enabled/jsowncloud.com':
            service.model.data.result = 'FAILED : {} {} {}'.format('test_ays_build',
                                        'owncloud webpage in not enabled for nginx',
                                         str(sys.exc_info()[:2]))
            service.save()
            return
        check = cuisine.core.run('ps aux | grep php-fpm | grep -v grep | wc -l')
        if check[1] < 1:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_ays_build',
                                        'No process running for php-fpm',
                                        str(sys.exc_info()[:2]))
            service.save()
            return
        # we can add more checks to render owncloud page
        service.model.data.result = 'OK : {} '.format('test_ays_build')
    except:
        service.model.data.result = 'ERROR : {} {}'.format('test_ays_build', str(sys.exc_info()[:2]))
    log.info('Test Ended')
    service.save()
