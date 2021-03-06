def install(job):
    import os
    import yaml

    service = job.service
    cuisine = service.executor.cuisine
    args = service.model.data

    # Install dependencies
    cuisine.development.js8.install()
    cuisine.apps.redis.build(reset=True)
    cuisine.apps.redis.start(maxram="200mb")
    cuisine.solutions.cockpit.install_deps()

    # Configure ays
    AYS_CONFIG_LOCATION = "$cfgDir/ays/ays.conf"
    _conf = {
        "redis": {
            "host": "localhost",
            "port": 6379,
        },
        "metadata": {
            "jumpscale": {
                "url": "https://github.com/Jumpscale/ays_jumpscale8",
                "branch": "master"
            }
        }
    }

    ays_conf = yaml.dump(_conf, default_flow_style=False)
    cuisine.core.dir_ensure(os.path.dirname(AYS_CONFIG_LOCATION))
    cuisine.core.file_write(location=AYS_CONFIG_LOCATION, content=ays_conf, replaceArgs=True)
    pm = cuisine.processmanager.get("tmux")
    pm.ensure(name="ays_daemon", cmd="ays start -c {config}".format(config=AYS_CONFIG_LOCATION))

    cuisine.development.git.pullRepo('https://github.com/Jumpscale/jscockpit', '$codeDir/github/jumpscale/jscockpit')

    # Prepare ssh keys
    dns = service.producers['sshkey'][0]
    DNS_PATH = '/root/.ssh/dns_rsa'
    cuisine.core.file_write(location=DNS_PATH,
                            content=dns.model.data.keyPriv,
                            mode=600)
    cuisine.core.run("ssh-keygen -y -f {dns_path} > {dns_path}.pub".format(dns_path=DNS_PATH))

    # Prepare the conifg.yaml
    g8_options = {}
    for option in args.g8:
        key_address = option.split('|', 1)
        g8_options[key_address[0]] = {"address": key_address[1]}

    deployer_cfg = {
        "bot": {
            "token": args.botToken
        },
        "g8": g8_options,
        "oauth": {
            "port": args.oauthPort,
            "itsyouonlinehost": args.oauthItsyouonlinehost,
            "client_id": args.oauthClient,
            "host": args.oauthHost,
            "client_secret": args.oauthSecret,
            "redirect_uri": args.oauthRedirect,
        },
        "dns": {
            "sshkey": DNS_PATH,
        }
    }
    deployer_cfg = yaml.dump(deployer_cfg, default_flow_style=False)
    cuisine.core.file_write(location="$codeDir/github/jumpscale/jscockpit/deployer_bot/config.yaml",
                            content=deployer_cfg,
                            replaceArgs=True)

    cmd = "cd $codeDir/github/jumpscale/jscockpit/deployer_bot && ./telegram-bot -c config.yaml"
    pm.ensure(name="deployer", cmd=cmd)
