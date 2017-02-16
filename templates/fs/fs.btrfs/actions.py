def init_actions_(service, args):
    """
    this needs to returns an array of actions representing the depencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """

    # some default logic for simple actions
    return {
        'autoscale': ['install']
    }

def install(job):
    import re
    service = job.service
    # List available devices
    os_svc = service.producers['os'][0]
    nod = os_svc.producers['node'][0]
    if nod.model.data.osImage == 'Ubuntu 14.04 x64':
        service.executor.cuisine.package.multiInstall(["btrfs-tools"])
        rc, out, err = service.executor.cuisine.core.run('lsblk -d -P  -o NAME,FSTYPE,MOUNTPOINT')
        out = out.split("\n")
        disks = {
            "blockdevices": [],
        }
        for val in out:
            obj = {}
            obj['name'], obj['fstype'], obj['mountpoint'] = [value.strip('"')for value in re.findall(r'"[a-z]*[0-9]*"', val)]
            disks["blockdevices"].append(obj)
    else:
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
    if master['mountpoint'] is None or master['mountpoint'] == "":
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
            cmd = 'btrfs device add -f /dev/%s %s' % (device['name'], service.model.data.mount)
            code, _, err = service.executor.cuisine.core.run(cmd)
            if code != 0:
                raise RuntimeError('failed to add device %s to fs: %s' % (
                    device['name'],
                    err)
                )


def autoscale(job):
    service = job.service
    repo = service.aysrepo
    exc = service.executor
    cuisine = exc.cuisine
    code, out, err = cuisine.core.run('btrfs filesystem  usage -b {}'.format(service.model.data.mount), die=False)
    if code != 0:
        raise RuntimeError('failed to get device usage: %s', err)
    # get free space.
    import re
    match = re.search('Free[^:]*:\s+(\d+)', out)
    if match is None:
        raise RuntimeError('failed to get free space')
    free = int(match.group(1)) / (1024 * 1024)  # MB.
    node = None
    for parent in service.parents:
        if parent.model.role == 'node':
            node = parent
            break
    if node is None:
        raise RuntimeError('failed to find the parent node')
    # DEBUG, set free to 0
    current_disks = list(node.model.data.disk)
    if free < service.model.data.threshold:
        # add new disk to the array.
        args = {
            'size': service.model.data.incrementSize,
            'prefix': 'autoscale',
        }
        adddiskjob = node.getJob('add_disk')
        adddiskjob.model.args = args
        adddiskjob.executeInProcess()
    node = repo.serviceGet(node.model.role, node.name)
    new_disks = list(node.model.data.disk)

    added = set(new_disks).difference(current_disks)
    # if len(added) != 1:
    #     raise RuntimeError('failed to find the new added disk (disks found %d)', len(added))
    #TODO: add device to volume
    # get the disk object.
    if added:
        disk_name = added.pop()
        disk = None
        os_svc = service.producers['os'][0]
        nod = os_svc.producers['node'][0]
        for dsk in nod.producers.get('disk', []):
            if dsk.model.dbobj.name == disk_name:
                disk = dsk
                break
        if disk is None:
            raise RuntimeError('failed to find disk service instance')

        rc, out, err = cuisine.core.run("btrfs device add /dev/{devicename} {mountpoint}".format(devicename=disk.model.data.devicename, mountpoint=service.model.data.mount))
        if rc != 0:
            raise RuntimeError("Couldn't add device to /data")
