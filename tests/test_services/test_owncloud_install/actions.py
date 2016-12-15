###########################################
This service is not complete and not tested
###########################################
def init_actions_(service, args):
    """
    this needs to returns an array of actions representing the depencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """
    return {
        'test': ['install']
    }


def test(job):
    import unittest
    import time
    tc = unittest.TestCase('__init__')
    owncloud_url = 'testcloud.com'
    log = j.logger.get('test')
    log.addHandler(j.logger._LoggerFactory__fileRotateHandler('js8_test'))
    log.info('Test started')

    repo = j.atyourservice.repoGet("/opt/code/blueowncloud")
    # vm_exe  = repo.servicesFind(actor="os.ssh.ubuntu", name="bc")[0]
    # rc, out, err = vm_exe.executor.cuisine.core.run('docker ps -a') # check on out

    log.info('Check that tidb server is running on port 3306')
    tidbos = repo.servicesFind(actor='os.ssh.ubuntu', name='tidb')[0]
    out = tidbos.executor.cuisine.core.run("ps aux |  grep -o -F "tidb-server -P 3306" -m 1")
    tc.assertEqual(out[1], 'tidb-server -P 3306')

    log.info('Check that nginx is running')
    ocos = repo.servicesFind(actor="os.ssh.ubuntu", name="owncloud")[0]
    out = ocos.executor.cuisine.core.run("ps aux | grep -o -F "nginx: master process /opt/jumpscale8/apps/nginx/bin/nginx -c /optvar/cfg/nginx/etc/nginx.conf")
    tc.assertEqual(out[1], 'nginx: master process"
                            "/opt/jumpscale8/apps/nginx/bin/nginx"
                            "-c /optvar/cfg/nginx/etc/nginx.conf')

    log.info('Check that the owncloud site in enabled in nginx')
    out = ocos.executor.cuisine.core.run("ls /optvar/cfg/nginx/etc/sites-enabled")
    tc.assertEqual(out[1], owncloud_url)

    log.info('Check that the pid for the nginx don\'t change')
    out = ocos.executor.cuisine.core.run("sv status nginx | awk '{print$4}'")
    time.sleep(1)
    out2 = ocos.executor.cuisine.core.run("sv status nginx | awk '{print$4}'")
    tc.assertEqual(out[1], out[2])

    log.info('Check if the owncloud site can respond back')
    ocos.executor.cuisine.core.run('echo "127.0.0.1 %s" >> /etc/hosts' % owncloud_url)
    out = ocos.executor.cuisine.core.run("curl %s -L | grep -o -F GreenITGlobe" % owncloud_url)
    tc.assertEqual(out[1], 'GreenITGlobe')

    log.info('Test Ended')



