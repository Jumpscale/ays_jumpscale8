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
        'disk': list(service.model.data.disk)
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

    # app docker
    docker = {
        'image': 'jumpscale/ubuntu1604',
        'hostname': service.model.data.domain,
        'fs': ['fuse', 'data'],
        'os': service.name,
        'ports': [
            '2201:22',
            '8000:8000'
        ],
        'volumes': [
            '/mnt/fs/opt/:/opt/',
            '/data:/data'
        ]
    }

    repo.actorGet('node.docker').serviceCreate('app', docker)
    repo.actorGet('os.ssh.ubuntu').serviceCreate('app', {'node': 'app'})

    # app
    app = {
        'os': 'app',
        'domain': service.model.data.domain,
        'storage.data': '/data/data',
        'storage.meta': '/data/meta'
    }

    repo.actorGet('scality').serviceCreate('app', app)

    # caddy proxy
    caddy = {
        'image': 'jumpscale/ubuntu1604',
        'hostname': 'caddy',
        'fs': ['fuse'],
        'os': service.name,
        'ports': [
            '2202:22',
            '80:80'
        ],
        'volumes': [
            '/mnt/fs/opt/:/opt/',
        ]
    }

    repo.actorGet('node.docker').serviceCreate('caddy', caddy)
    repo.actorGet('os.ssh.ubuntu').serviceCreate('caddy', {'node': 'caddy'})

    proxy = {
        'src': '/',
        'dst': ['172.17.0.1:8000']
    }

    repo.actorGet('caddy_proxy').serviceCreate('proxy', proxy)

    caddy_service = {
        'os': 'caddy',
        'fs': 'cockpit',
        'email': 'mail@fake.com',
        'hostname': ':80',
        'caddy_proxy': ['proxy']
    }

    repo.actorGet('caddy').serviceCreate('caddy', caddy_service)
