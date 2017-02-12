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
        from ast import literal_eval
        log = j.logger.get('test')
        log.addHandler(j.logger._LoggerFactory__fileRotateHandler('tests'))
        service = job.service
        branch = service.model.data.branch
        cuisine = service.executor.cuisine
        log.info('Installing jumpscale on the VM')
        cuisine.core.run('apt-get update')
        cuisine.core.run('echo Y | apt-get install curl')
        cuisine.core.run('curl -k https://raw.githubusercontent.com/Jumpscale/'
                         'jumpscale_core8/{}/install/install.sh > install.sh'.format(branch))
        if branch != "master":
            cuisine.core.run('export JSBRANCH="{}"'.format(branch))
        cuisine.core.run('bash install.sh')
        time.sleep(50)

        log.info('Check if js is working, should succeed')
        output = cuisine.core.run('js "print(j.sal.fs.getcwd())"')
        if output[1] != '/':
            service.model.data.result = 'FAILED : {} {}'.format('test_js8_install', str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('Check if directories under /optvar/ is as expected')
        output = cuisine.core.run('ls /optvar')
        if output[1] != 'cfg\ndata':
            service.model.data.result = 'FAILED : {} {}'.format('test_js8_install', str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('Check if directories under /opt/jumpscale8/ is as expected')
        output = cuisine.core.run('ls /opt/jumpscale8/')
        if output[1] != 'bin\nenv.sh\nlib':
            service.model.data.result = 'FAILED : {} {}'.format('test_js8_install', str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('Compare js.dir to j.tools.cuisine.local.core.dir_paths, should be the same')
        output = cuisine.core.run('js "print(j.dirs)"')
        output2 = cuisine.core.run('js "print(j.tools.cuisine.local.core.dir_paths)"')

        str_list = output[1].split('\n')
        # remove empty strings found in a list
        for i in str_list:
            var = "".join(i.split())
            str_list[str_list.index(i)] = var.split(':')
        dict1 = dict(str_list)
        dict2 = literal_eval(output2[1])

        if dict1['homeDir'] != dict2['homeDir']:
            service.model.data.result = 'FAILED : {} {}'.format('test_js8_install', str(sys.exc_info()[:2]))
            service.save()
            return
        if dict1['base'] != dict2['base']:
            service.model.data.result = 'FAILED : {} {}'.format('test_js8_install', str(sys.exc_info()[:2]))
            service.save()
            return
        if dict1['appDir'].replace('/', '') != dict2['appDir'].replace('/', ''):
            service.model.data.result = 'FAILED : {} {}'.format('test_js8_install', str(sys.exc_info()[:2]))
            service.save()
            return
        if dict1['libDir'].replace('/', '') != dict2['libDir'].replace('/', ''):
            service.model.data.result = 'FAILED : {} {}'.format('test_js8_install', str(sys.exc_info()[:2]))
            service.save()
            return
        if dict1['binDir'].replace('/', '') != dict2['binDir'].replace('/', ''):
            service.model.data.result = 'FAILED : {} {}'.format('test_js8_install', str(sys.exc_info()[:2]))
            service.save()
            return
        if dict1['cfgDir'].replace('/', '') != dict2['cfgDir'].replace('/', ''):
            service.model.data.result = 'FAILED : {} {}'.format('test_js8_install', str(sys.exc_info()[:2]))
            service.save()
            return
        if dict1['codeDir'].replace('/', '') != dict2['codeDir'].replace('/', ''):
            service.model.data.result = 'FAILED : {} {}'.format('test_js8_install', str(sys.exc_info()[:2]))
            service.save()
            return
        if dict1['jsLibDir'].replace('/', '') != dict2['jsLibDir'].replace('/', ''):
            service.model.data.result = 'FAILED : {} {}'.format('test_js8_install', str(sys.exc_info()[:2]))
            service.save()
            return
        if dict1['pidDir'].replace('/', '') != dict2['pidDir'].replace('/', ''):
            service.model.data.result = 'FAILED : {} {}'.format('test_js8_install', str(sys.exc_info()[:2]))
            service.save()
            return
        if dict1['logDir'].replace('/', '') != dict2['logDir'].replace('/', ''):
            service.model.data.result = 'FAILED : {} {}'.format('test_js8_install', str(sys.exc_info()[:2]))
            service.save()
            return
        if dict1['varDir'].replace('/', '') != dict2['varDir'].replace('/', ''):
            service.model.data.result = 'FAILED : {} {}'.format('test_js8_install', str(sys.exc_info()[:2]))
            service.save()
            return
        if dict1['tmplsDir'].replace('/', '') != dict2['tmplsDir'].replace('/', ''):
            service.model.data.result = 'FAILED : {} {}'.format('test_js8_install', str(sys.exc_info()[:2]))
            service.save()
            return
        service.model.data.result = 'OK : {} '.format('test_js8_install')
    except:
        service.model.data.result = 'ERROR : {} {}'.format('test_js8_install', str(sys.exc_info()[:2]))
    log.info('Test Ended')
    service.save()
