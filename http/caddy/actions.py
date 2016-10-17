def install(job):
    service = job.service
    cuisine = job.service.executor.cuisine

    cuisine.core.run('touch $binDir/caddy')

    name = "caddy_%s" % service.name
    proxies_dir = cuisine.core.args_replace('$cfgDir/caddy/%s/proxies' % name)
    cuisine.core.dir_ensure(proxies_dir)

    for proxy_info in service.producers.get('caddy_proxy', []):
        dst = ' '.join(proxy_info.model.data.dst)
        cfg = 'proxy %s %s {\n' % (proxy_info.model.data.src, dst)
        cfg += '\tfail_timeout %s\n' % proxy_info.model.data.failTimeout
        cfg += '\tmax_fails %s\n' % proxy_info.model.data.maxFails
        if proxy_info.model.data.without != '':
            cfg += '\twithout %s\n' % proxy_info.model.data.without
        for header in proxy_info.model.data.headerUpstream:
            cfg += '\theader_upstream %s\n' % header
        for header in proxy_info.model.data.headerDownstream:
            cfg += '\theader_downstream %s\n' % header
        cfg += '}\n'

        cuisine.core.file_write(proxies_dir + '/%s' % proxy_info.name, cfg)

    cfg = ''
    cfg += service.model.data.hostname + '\n'
    if service.model.data.gzip:
        cfg += 'gzip\n'
    cfg += 'import %s/*\n' % proxies_dir

    conf_location = cuisine.core.args_replace('$cfgDir/caddy/%s/Caddyfile' % name)
    cuisine.core.file_write(conf_location, cfg)

    bin_location = cuisine.core.command_location('caddy')
    cmd = '{bin} -conf {conf} --agree --email {email}'.format(
        bin=bin_location,
        conf=conf_location,
        email=service.model.data.email)
    if service.model.data.stagging is True:
        # enable stating environment, remove for prodction
        cmd += ' -ca https://acme-staging.api.letsencrypt.org/directory'
    cuisine.processmanager.ensure("caddy_%s" % service.name, cmd=cmd, path='$cfgDir/caddy/%s' % name)


def start(job):
    cuisine = job.service.cuisine
    cuisine.processmanager.start("caddy_%s" % service.name)


def stop(job):
    cuisine = job.service.cuisine
    cuisine.processmanager.stop("caddy_%s" % service.name)
