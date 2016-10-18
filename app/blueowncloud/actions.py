def init(job):
    service = job.service
    repo = service.aysrepo

    # ovc node.
    vm = {
        'os.image': 'g8os-test-1604',
        'bootdisk.size': 10,
        'vdc': service.parent.name,
        'memory': 4,
        'ports': [
            '2200:22',
            '2201:2201',
            '2202:2202',
            '80:80'
        ],
        'datadisks': list(service.model.data.datadisks)
    }

    repo.actorGet('node.ovc').serviceCreate(service.name, vm)
    repo.actorGet('os.ssh.ubuntu').serviceCreate(service.name, {'node': service.name})

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
        'fs': ['fuse', 'data'],
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
        ]
    }

    repo.actorGet('node.docker').serviceCreate('owncloud', owncloud)
    repo.actorGet('os.ssh.ubuntu').serviceCreate('owncloud', {'node': 'owncloud'})

    repo.actorGet('tidb').serviceCreate('tidb', {'os': 'tidb', 'clusterId': '1'})

    owncloudconf = {
        'os': 'owncloud',
        'tidb': 'tidb',
        'tidbuser': 'root',
        'tidbpassword': '',
        'sitename': service.model.data.domain,
        'owncloudAdminUser': 'admin',
        'owncloudAdminPassword': 'admin'
    }

    repo.actorGet('owncloud').serviceCreate('own1', owncloudconf)
