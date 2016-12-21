def init(job):
    service = job.service
    repo = service.aysrepo
    disksizes = list(service.model.data.datadisks)
    disks = []
    for idx, size in enumerate(disksizes):
        disk_name = 'disk-%s' % idx
        repo.actorGet('disk.ovc').serviceCreate(disk_name, {'size': size})
        disks.append(disk_name)

    # ovc node.
    vm = {
        'os.image': 'Ubuntu 16.04 x64',
        'bootdisk.size': 10,
        'vdc': service.parent.name,
        'memory': 4,
        'ports': [
            '2200:22',
            '2201:2201',
            '2202:2202',
            '80:80'
        ],
        'disk': disks
    }

    nodevm = repo.actorGet('node.ovc').serviceCreate(service.name, vm)
    repo.actorGet('os.ssh.ubuntu').serviceCreate(service.name, {'node': service.name})
    repo.actorGet('app_docker').serviceCreate('appdocker', {'os': service.name})

    # filesystem
    # 1- fuse
    fuse_cfg = {
        'mount.namespace': 'sandbox_ub1604',
        'mount.mountpoint': '/mnt/fs',
        'mount.flist': 'https://stor.jumpscale.org/stor2/flist/sandbox_ub1604/opt.flist',
        'mount.mode': 'ol',
        'mount.trimbase': False,
        'backend.path': '/mnt/fs_backend/opt',
        'backend.namespace': 'sandbox_ub1604',
        'backend.cleanup.cron': "@every 1h",
        'backend.cleanup.old': 24,
        'store.url': 'https://stor.jumpscale.org/stor2'
    }

    repo.actorGet('vfs_config').serviceCreate('opt', fuse_cfg)

    fuse = {
        'os': service.name,
        'vfs_config': ['opt']
    }

    repo.actorGet('fs.g8osfs').serviceCreate('fuse', fuse)

    # 2- btrfs
    btrfs = {
        'os': service.name,
        'mount': '/data'
    }

    repo.actorGet('fs.btrfs').serviceCreate('data', btrfs)

    # tidb docker
    tidb = {
        'image': 'jumpscale/ubuntu1604',
        'hostname': service.model.data.domain,
        'fs': ['fuse'],
        'os': service.name,
        'ports': [
            '2201:22',
            '3306:3306'
        ],
        'volumes': [
            '/mnt/fs/opt/:/opt/',
        ]
    }

    repo.actorGet('node.docker').serviceCreate('tidb', tidb)
    repo.actorGet('os.ssh.ubuntu').serviceCreate('tidb', {'node': 'tidb'})

    # app docker
    owncloud = {
        'image': 'jumpscale/ubuntu1604',
        'hostname': service.model.data.domain,
        'fs': ['fuse', 'data'],
        'os': service.name,
        'ports': [
            '2202:22',
            '80:80'
        ],
        'volumes': [
            '/mnt/fs/opt/:/opt/',
            '/data/:/data/',
        ]
    }

    repo.actorGet('node.docker').serviceCreate('owncloud', owncloud)
    repo.actorGet('os.ssh.ubuntu').serviceCreate('owncloud', {'node': 'owncloud'})

    repo.actorGet('tidb').serviceCreate('tidb', {'os': 'tidb', 'clusterId': '1'})

    # app
    machineip = nodevm.model.data.ipPublic
    # ip2num
    machineuniquenumber = j.sal.nettools.ip_to_num(machineip)
    domain = "{appname}-{num}.gigapps.io".format(appname=service.model.data.appname, num=machineuniquenumber)

    owncloudconf = {
        'os': 'owncloud',
        'tidb': 'tidb',
        'tidbuser': 'root',
        'tidbpassword': '',
        'sitename': domain,
        'owncloudAdminUser': 'admin',
        'owncloudAdminPassword': 'admin'
    }

    repo.actorGet('owncloud').serviceCreate('own1', owncloudconf)
