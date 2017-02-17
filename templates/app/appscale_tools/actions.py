def install(job):
    """
    Installing appscale tools
    """
    service = job.service
    cuisine = service.executor.cuisine
    data = service.model.data

    cuisine.apps.appscale.build_tools(data.appscaletag)

    # Pre-authenticate all used nodes
    all_nodes = set()
    for key in data.to_dict().keys():
        if key.endswith("Node"):
            node = getattr(data, key)
            if isinstance(node, str):
                all_nodes.add(node)
            else:
                for n in node:
                    all_nodes.add(n)

    key_path = cuisine.ssh.keygen(name="id_rsa")
    for node in all_nodes:
        _os = service.aysrepo.servicesFind(actor='os.*', name=node)[0]
        _node = service.aysrepo.servicesFind(actor='node.*', name=node)[0]
        _, out, _ = cuisine.core.run("cat %s" % key_path)
        _os.executor.cuisine.ssh.authorize(user="root", key=out)

        cuisine.core.run("ssh-keyscan %s >> /root/.ssh/known_hosts" % _node.model.data.ipPrivate, die=True)

    APPSCALEFILE_LOCATION = "/root"
    appscale_cfg = {
        "ips_layout": {
            "master": service.aysrepo.servicesFind(actor='node.*', name=data.masterNode)[0].model.data.ipPrivate,
            "search": service.aysrepo.servicesFind(actor='node.*', name=data.searchNode)[0].model.data.ipPrivate,
        },
        "test": True,
    }
    for key in ("appengine", "database", "zookeeper"):
        for node in getattr(data, key + "Node"):
            ip = service.aysrepo.servicesFind(actor='node.*', name=node)[0].model.data.ipPrivate
            if key not in appscale_cfg.keys():
                appscale_cfg["ips_layout"][key] = [ip]
            else:
                appscale_cfg["ips_layout"][key].append(ip)

    appscale_cfg = j.data.serializer.yaml.dumps(appscale_cfg)

    cuisine.core.file_write(location="/%s/AppScalefile" % APPSCALEFILE_LOCATION, content=appscale_cfg)
    cuisine.core.dir_ensure("/home/cloudscalers/.ssh")
    appscale_up_cmd = "cd {location} && appscale up".format(location=APPSCALEFILE_LOCATION)

    # Hack: paramiko use the host keys for the remote ssh connection
    appscale_up_cmd = """
    set -ex
    eval `ssh-agent`
    ssh-add /root/.ssh/id_rsa
    cd /root && appscale up
    """
    cuisine.core.run(appscale_up_cmd, die=True)
