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
    tc = unittest.TestCase('__init__')
    log = j.logger.get('test')
    log.addHandler(j.logger._LoggerFactory__fileRotateHandler('scality_test'))
    log.info('Test started')
    service = job.service
    repo = service.aysrepo
    scality = repo.servicesFind(actor='scality', name='app')[0]
    keyaccess = scality.model.data.keyAccess
    keysecret = scality.model.data.keySecret
    s3vm = repo.servicesFind(actor='os.ssh.ubuntu', name='s3vm')[0]
    s3vm_exe = s3vm.executor.cuisine

    log.info('Install s3cmd on the s3_vm and connecting it to s3 server')
    s3vm_exe.core.run('echo "Y" | apt-get install s3cmd')
    config = """
    [default]
    access_key = {}
    secret_key = {}
    host_base = localhost
    host_bucket = localhost
    signature_v2 = True
    use_https = False
    """.format(keyaccess, keysecret)
    s3vm_exe.core.run("cd /root; echo '{}' > .s3cfg".format(config))

    log.info('Creating bucket')
    bucket = s3vm_exe.core.run("s3cmd mb s3://test")
    tc.assertEqual(bucket[1], "Bucket 's3://test/' created")

    log.info('Put file into bucket')
    s3vm_exe.core.run('cd /root; touch test_file')
    s3vm_exe.core.run('cd /root; s3cmd put test_file s3://test/check')

    log.info('Get File from bucket')
    s3vm_exe.core.run('s3cmd get s3://test/check')
    check = s3vm_exe.core.run('ls check |  wc -l')
    tc.assertEqual(check[1], '1')

    log.info('Test Ended')

