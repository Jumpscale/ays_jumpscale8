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
    log.addHandler(j.logger._LoggerFactory__fileRotateHandler('lim_iops_test'))
    log.info('Test started')
    service = job.service
    vm_os = service.producers.get('os')[0]
    vm_exe = vm_os.executor.cuisine

    log.info('Install fio')
    vm_exe.core.run('apt-get update')
    vm_exe.core.run('echo "Y" | apt-get install fio')

    def fio_run(out_file, disk):
        fio_cmd = "fio --ioengine=libaio --group_reporting --filename=/dev/{1} "\
                  "--runtime=30 --readwrite=randrw --size=500M --name=test{0} "\
                  "--output={0}".format(out_file, disk)
        return fio_cmd

    def check_iops(executor, out_file, iops_limit):
        out = vm_exe.core.run("cat %s | grep -o 'iops=[0-9]\{1,\}' | cut -d '=' -f 2" % out_file)
        list = out[1].split('\n')
        int_list = [int(i) for i in list if int(i) > iops_limit]
        return len(int_list)

    log.info('Run fio on vdb, iops should be less than maxIOPS')
    vm = service.producers['node'][0]
    disk = vm.producers['disk'][0]
    maxIOPS = disk.model.data.maxIOPS
    vm_exe.core.run(fio_run('b1', 'vdb'))
    iops = check_iops(vm_exe, 'b1', maxIOPS)
    tc.assertEqual(iops, 0)

    log.info('Create another data disk (vdc) and set max_iops to 1000')
    vdc = vm.producers['vdc'][0]
    g8client = vdc.producers["g8client"][0]
    client = j.clients.openvcloud.getFromService(g8client)
    acc = client.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)
    machine = space.machines[vm.name]
    disk_id = machine.add_disk(name='disk_c', description='test', size=50, type='D')
    machine.disk_limit_io(disk_id, 1000)

    log.info('Run fio on vdc, iops should be less than 1000')
    vm_exe.core.run(fio_run('c1', 'vdc'))
    iops = check_iops(vm_exe, 'c1', 1000)
    tc.assertEqual(iops, 0)

    log.info('Run fio on vdc, iops should be less than 500')
    machine.disk_limit_io(disk_id, 500)
    vm_exe.core.run(fio_run('c2', 'vdc'))
    iops = check_iops(vm_exe, 'c2', 500)
    tc.assertEqual(iops, 0)

    log.info('Test Ended')
