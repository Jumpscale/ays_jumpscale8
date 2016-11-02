def init(job):
    service = job.service
    repo = service.aysrepo

    node = service.aysrepo.servicesFind(actor='node.*', name=service.model.data.hostNode)[0]
    os = service.aysrepo.servicesFind(actor='os.*', name=service.model.data.hostNode)[0]

    # filesystem
    # 1- fuse
    fuse_cfg = {
        'mount.namespace': 'sandbox_ub1604',
        'mount.mountpoint': '/opt',
        'mount.flist': 'https://stor.jumpscale.org/stor2/flist/aysbuild/test.flist',
        'mount.mode': 'ol',
        'mount.trimbase': True,
        'mount.trim': '/opt',
        'backend.path': '/mnt/fs_backend/opt',
        'backend.namespace': 'aysbuild',
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
        'src': '/',
        'dst': ['127.0.0.1:82']
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
        'redis': redis.name,
        'oauth.enabled': True,
        'oauth.client_id': service.model.data.oauthClientId,
        'oauth.scope': 'user:email:main,user:memberof:{organization}'.format(organization=service.model.data.oauthOrganization),
        'oauth.secret': service.model.data.oauthClientSecret,
        'oauth.client_url': 'https://itsyou.online/v1/oauth/authorize',
        'oauth.client_user_info_url': 'https://itsyou.online/api/users',
        'oauth.provider': 'itsyou.online',
        'oauth.default_groups': ['admin', 'user'],
        'oauth.organization': service.model.data.oauthOrganization,
        'oauth.redirect_url': "https://{domain}/restmachine/system/oauth/authorize".format(domain=service.model.data.domain),
        'oauth.token_url': 'https://itsyou.online/v1/oauth/access_token'
    }

    repo.actorGet('portal').serviceCreate('main', portal)

    ayscockpit_cfg = {
        'os': os.name,
        'fs': fs.name,
        'redis': redis.name,

        'domain': service.model.data.domain,

        'oauth.client_secret': service.model.data.oauthClientSecret,
        'oauth.client_id': service.model.data.oauthClientId,
        'oauth.organization': service.model.data.oauthOrganization,
        'oauth.jwt_key': service.model.data.oauthJwtKey,
        'oauth.redirect_url': 'https://{domain}/api/oauth/callback'.format(domain=service.model.data.domain),

        'api.host': '127.0.0.1',
        'api.port': 5000,
    }

    repo.actorGet('ayscockpit').serviceCreate('main', ayscockpit_cfg)
