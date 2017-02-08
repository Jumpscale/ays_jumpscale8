def init(job):
    service = job.service
    repo = service.aysrepo
    # node_mgmt = service.aysrepo.servicesFind(actor='node.*', name=service.model.data.osmgmt)[0]
    os_mgmt = service.aysrepo.servicesFind(actor='os.*', name=service.model.data.osmgmt)[0]

    # node_master = service.aysrepo.servicesFind(actor='node.*', name=service.model.data.osmaster)[0]
    os_master = service.aysrepo.servicesFind(actor='os.*', name=service.model.data.osmaster)[0]

    appscale_tools_cfg = {
        'os': os_mgmt.name,
        'appscaletag': 'dev',
    }

    repo.actorGet('appscale_tools').serviceCreate('tools', appscale_tools_cfg)

    appscale_cfg = {
        'os': os_master.name,
        'appscaletag': 'dev',
    }

    repo.actorGet('appscale').serviceCreate('appscale', appscale_cfg)
