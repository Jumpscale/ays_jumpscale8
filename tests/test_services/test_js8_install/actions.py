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
    from ast import literal_eval
    tc = unittest.TestCase('__init__')
    log = j.logger.get('test')
    log.addHandler(j.logger._LoggerFactory__fileRotateHandler('js8_test'))
    service = job.service
    branch = service.model.data.branch
    cuisine = service.executor.cuisine
    log.info('Installing jumpscale on the VM')
    cuisine.core.run('apt-get update')
    cuisine.core.run('echo Y | apt-get install curl')
    cuisine.core.run('curl -k https://raw.githubusercontent.com/Jumpscale/'
                     'jumpscale_core8/{}/install/install.sh > install.sh'.format(branch))
    if branch != "master":
        cuisine.core.run('export JSBRANCH = "{}"'.format(branch))
    cuisine.core.run('bash install.sh')
    time.sleep(50)

    log.info('Check if js is working, should succeed')
    output = cuisine.core.run('js "print(j.sal.fs.getcwd())"')
    tc.assertEqual(output[1], '/')

    log.info('Check if directories under /optvar/ is as expected')
    output = cuisine.core.run('ls /optvar')
    tc.assertEqual(output[1], 'cfg\ndata')

    log.info('Check if directories under /opt/jumpscale8/ is as expected')
    output = cuisine.core.run('ls /opt/jumpscale8/')
    tc.assertEqual(output[1], 'bin\nenv.sh\nlib')

    def convert_string_to_dict(string, split):
        str_list = string.split(split)
        #remove empty strings found in a list
        for i in str_list:
            var = "".join(i.split())
            str_list[str_list.index(i)] = var.split(':')
        return dict(str_list)

    log.info('Compare js.dir to j.tools.cuisine.local.core.dir_paths, should be the same')
    output = cuisine.core.run('js "print(j.dirs)"')
    output2 = cuisine.core.run('js "print(j.tools.cuisine.local.core.dir_paths)"')
    dict1 = convert_string_to_dict(output[1], '\n')
    dict2 = literal_eval(output2[1])
    tc.assertEqual(dict1['HOMEDIR'], dict2['HOMEDIR'])
    tc.assertEqual(dict1['base'], dict2['base'])
    tc.assertEqual(dict1['JSAPPSDIR'].replace('/', ''), dict2['JSAPPSDIR'].replace('/', ''))
    tc.assertEqual(dict1['LIBDIR'].replace('/', ''), dict2['LIBDIR'].replace('/', ''))
    tc.assertEqual(dict1['BINDIR'].replace('/', ''), dict2['BINDIR'].replace('/', ''))
    tc.assertEqual(dict1['JSCFGDIR'].replace('/', ''), dict2['JSCFGDIR'].replace('/', ''))
    tc.assertEqual(dict1['CODEDIR'].replace('/', ''), dict2['CODEDIR'].replace('/', ''))
    tc.assertEqual(dict1['JSLIBDIR'].replace('/', ''), dict2['JSLIBDIR'].replace('/', ''))
    tc.assertEqual(dict1['PIDDIR'].replace('/', ''), dict2['PIDDIR'].replace('/', ''))
    tc.assertEqual(dict1['LOGDIR'].replace('/', ''), dict2['LOGDIR'].replace('/', ''))
    tc.assertEqual(dict1['VARDIR'].replace('/', ''), dict2['VARDIR'].replace('/', ''))
    tc.assertEqual(dict1['TEMPLATEDIR'].replace('/', ''), dict2['TEMPLATEDIR'].replace('/', ''))