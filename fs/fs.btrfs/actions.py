def install(job):
    service = job.service
    # List available devices

    code, out, err = service.executor.cuisine.core.run('lsblk -J  -o NAME,FSTYPE,MOUNTPOINT')
    if code != 0:
        raise RuntimeError('failed to list bulk devices: %s' % err)

    disks = j.data.serializer.json.loads(out)
    btrfs_devices = []
    for device in disks['blockdevices']:
        if not device['name'].startswith('vd') or device['name'] == 'vda':
            continue
        btrfs_devices.append(device)

    btrfs_devices.sort(key=lambda e: e['name'])
    if len(btrfs_devices) == 0:
        raise RuntimeError('no data disks on machine')

    master = btrfs_devices[0]
    if master['fstype'] != 'btrfs':
        # creating the filesystem on all of the devices.
        cmd = 'mkfs.btrfs -f %s' % ' '.join(map(lambda e: '/dev/%s' % e['name'], btrfs_devices))
        code, out, err = service.executor.cuisine.core.run(cmd)
        if code != 0:
            raise RuntimeError('failed to create filesystem: %s' % err)

    if master['mountpoint'] == None:
        service.executor.cuisine.core.dir_ensure(service.model.data.mount)
        cmd = 'mount /dev/%s %s' % (master['name'], service.model.data.mount)
        code, out, err = service.executor.cuisine.core.run(cmd)
        if code != 0:
            raise RuntimeError('failed to mount device: %s' % err)

    # Last thing is to check that all devices are part of the filesystem
    # in case we support hot plugging of disks in the future.
    code, out, err = service.executor.cuisine.core.run('btrfs filesystem show /dev/%s' % master['name'])
    if code != 0:
        raise RuntimeError('failed to inspect filesystem on device: %s' % err)

    # parse output.
    import re
    fs_devices = re.findall('devid\s+.+\s/dev/(.+)$', out, re.MULTILINE)
    for device in btrfs_devices:
        if device['name'] not in fs_devices:
            # add device to filesystem
            cmd = 'btfs device add -f /dev/%s %s' % (device['name'], service.model.data.mount)
            code, _, err = service.executor.cuisine.core.run(cmd)
            if code != 0:
                raise RuntimeError('failed to add device %s to fs: %s' % (
                    device['name'],
                    err)
                )
