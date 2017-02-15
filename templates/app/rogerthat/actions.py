def init(job):
    service = job.service
    repo = service.aysrepo

    data = service.model.data
    master_node = service.aysrepo.servicesFind(actor='os.*', name=data.masterNode)[0].name

    all_nodes = set()
    for key in data.to_dict().keys():
        if key.endswith("Node") and key != "mgmtNode":
            node = getattr(data, key)
            if isinstance(node, str):
                all_nodes.add(node)
            else:
                for n in node:
                    all_nodes.add(n)

    # Build appscale configuration
    appscale_cfg = {
        'os': list(all_nodes),
        'appscaletag': 'dev',
    }

    appscale = repo.actorGet('appscale').serviceCreate('appscale', appscale_cfg)

    # Build appscale_tools configuration
    appscale_tools_cfg = {
        'masterNode': master_node,
        'appscaletag': 'dev',
        'os': service.aysrepo.servicesFind(actor='os.*', name=data.mgmtNode)[0].name,
        'searchNode': service.aysrepo.servicesFind(actor='os.*', name=data.searchNode)[0].name
    }

    # extracting names of those nodes and add them to appscale_tools_cfg
    attrs = ("zookeeperNode", "databaseNode", "appengineNode")
    for attr in attrs:
        for node in getattr(data, attr):
            node_name = service.aysrepo.servicesFind(actor='os.*', name=node)[0].name
            if attr not in appscale_tools_cfg.keys():
                appscale_tools_cfg[attr] = [node_name]
            else:
                appscale_tools_cfg[attr].append(node_name)

    tools = repo.actorGet('appscale_tools').serviceCreate('tools', appscale_tools_cfg)
    tools.consume(appscale)
