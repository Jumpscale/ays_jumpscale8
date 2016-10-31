def init(job):
    service = job.service
    repo = service.aysrepo

    # ovc node.
    vm = {
        'vdc': service.parent.name,
        'os.image': 'Ubuntu 16.04 x64',
        'bootdisk.size': 50,
        'memory': 4,
        'ports': [
            '22',
            '80:80',
            '443:443'
        ]
    }

    node = repo.actorGet('node.ovc').serviceCreate('cockpit', vm)
    os = repo.actorGet('os.ssh.ubuntu').serviceCreate('cockpit', {'node': node.name})

    # filesystem
    # 1- fuse
    fuse_cfg = {
        'mount.namespace': 'sandbox_ub1604',
        'mount.mountpoint': '/opt',
        'mount.flist': 'https://stor.jumpscale.org/stor2/flist/sandbox_ub1604/opt.flist',
        'mount.mode': 'ol',
        'mount.trimbase': True,
        'mount.trim': '/opt',
        'backend.path': '/mnt/fs_backend/opt',
        'backend.namespace': 'sandbox_ub1604',
        'backend.cleanup.cron': "@every 1h",
        'backend.cleanup.old': 24,
        'store.url': 'https://stor.jumpscale.org/stor2'
    }

    vfs_config = repo.actorGet('vfs_config').serviceCreate('opt', fuse_cfg)

    fuse = {
        'os': os.name,
        'vfs_config': [vfs_config.name]
    }

    fs = repo.actorGet('fs.g8osfs').serviceCreate('fuse', fuse)

    dns_sshkey = repo.actorGet('sshkey').serviceCreate('dns', {'key.path': service.model.data.dnsSshkeyPath})
    dns_clients_names = []
    for i, addr in enumerate(['dns1.aydo.com', 'dns3.aydo.com', 'dns3.aydo.com']):
        name = "dns%s" % (i + 1)
        dns_clients_names.append(name)
        dns = {
            'addr': addr,
            'port': 32768,
            'sshkey': dns_sshkey.name,
            'login': 'root',
        }
        repo.actorGet('dnsclient').serviceCreate(name, dns)

    # only take that last part of the domain.
    # e.g: sub.domain.com -> we keep domain.com
    root_domain = '.'.join(service.model.data.domain.split('.')[-2:])
    # sub domain is the domain minus the root_domain
    subdomain = sub = service.model.data.domain[:-len(root_domain) - 1]
    dns_domain = {
        'dnsclient': dns_clients_names,
        'ttl': 600,
        'domain': root_domain,
        'a.records': ["{subdomain}:{node}".format(subdomain=subdomain, node=node.name)],
        'node': [node.name],
    }

    repo.actorGet('dns_domain').serviceCreate('cockpit', dns_domain)

    api = {
        'src': '/api',
        'dst': ['127.0.0.1:5000'],
        'without': '/api'
    }

    repo.actorGet('caddy_proxy').serviceCreate('10_api', api)

    api = {
        'src': '/api',
        'dst': ['127.0.0.1:82'],
        'without': '/api'
    }

    repo.actorGet('caddy_proxy').serviceCreate('99_portal', api)

    caddy_cfg = {
        'os': os.name,
        'fs': fs.name,
        'email': service.model.data.caddyEmail,
        'hostname': service.model.data.domain,
        'caddy_proxy': ['10_api', '99_portal'],
    }

    repo.actorGet('caddy').serviceCreate('main', caddy_cfg)

    mongodb_cfg = {
        'os': os.name,
        'fs': fs.name,
    }

    repo.actorGet('mongodb').serviceCreate('main', mongodb_cfg)

    redis_cfg = {
        'os': os.name,
        'fs': fs.name,
        'unixsocket': '/optvar/tmp/redis.sock',
        'maxram': 2000000,
        'appendonly': True,
    }

    redis = repo.actorGet('redis').serviceCreate('ays', redis_cfg)

    portal = {
        'os': os.name,
        'fs': fs.name,
        'redis': redis.name
    }

    repo.actorGet('portal').serviceCreate('main', portal)

    ayscockpit_cfg = {
        'os': os.name,
        'fs': fs.name,
        'redis': redis.name,
        'dns_domain': service.model.data.domain,
    }

    repo.actorGet('ayscockpit').serviceCreate('main', ayscockpit_cfg)
