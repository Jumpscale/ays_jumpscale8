from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()

cfg_templ = """server {
    listen       443 ssl;
    server_name  localhost;
    ssl on;
    ssl_certificate     %s;
    ssl_certificate_key %s;
    ssl_client_certificate %s;
    ssl_verify_client on;
    #access_log  logs/host.access.log  main;

    location /controller/ {
            proxy_pass http://%s/;
            # the proxy read timeout must be set to a value bigger than the long poll timeout (of 60s)
            # other wise agent will start getting Bad Gateway errors.
            proxy_read_timeout 90s;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

    }
}"""


class Actions(ActionsBase):

    def configure(self, service_obj):
        if 'ac' not in service_obj.producers:
            j.events.inputerror_critical(msg="This service should consume an agentcontroller2 with role ac", category="agentcontroller2_keys")

        ac = service_obj.producers['ac'][0]

        # the generated keys and certificate will be store in the consumed agentcontroller2 folder
        server_cert = j.sal.fs.joinPaths(ac.path, 'server.crt')
        server_csr = j.sal.fs.joinPaths(ac.path, 'server.csr')
        server_key = j.sal.fs.joinPaths(ac.path, 'server.key')

        print("Generating server key...")
        cmd = 'openssl genrsa -out %s 2048 || exit 1' % server_key
        print(cmd)
        j.sal.process.execute(cmd, dieOnNonZeroExitCode=True, outputToStdout=False, useShell=False, ignoreErrorOutput=False)

        print("Generating server certificate signing request...")
        cmd = 'openssl req -new -key %s -out %s ' % (server_key, server_csr)
        cmd += '-subj "/C=$(country)/ST=$(state)/L=$(locality)/O=$(organisation)/CN=$(commonname)" || exit 1'
        print(cmd)
        j.sal.process.execute(cmd, dieOnNonZeroExitCode=True, outputToStdout=False, useShell=False, ignoreErrorOutput=False)

        print("Self signing the certificate")
        cmd = 'openssl x509 -req -days 3650 -in %s -signkey %s -out %s || exit 1' % (server_csr, server_key, server_cert)
        print(cmd)
        j.sal.process.execute(cmd, dieOnNonZeroExitCode=True, outputToStdout=False, useShell=False, ignoreErrorOutput=False)

        # save SSL info into agentcontroller hrd. So agent that consume agencontroller can use these information to 
        # generate client certificate
        ac.hrd.set('ssl.country', service_obj.hrd.getStr('country'))
        ac.hrd.set('ssl.state', service_obj.hrd.getStr('state'))
        ac.hrd.set('ssl.locality', service_obj.hrd.getStr('locality'))
        ac.hrd.set('ssl.organisation', service_obj.hrd.getStr('organisation'))
        ac.hrd.set('ssl.commonname', service_obj.hrd.getStr('commonname'))

        if 'ws' in service_obj.producers:
            cwd = j.sal.fs.getcwd()
            for ws in service_obj.producers['ws']:
                cfg = ''
                for ac in service_obj.producers['ac']:
                    ac_host = ac.hrd.getStr('param.webservice.host')

                    cfg += "\n "+cfg_templ % (server_cert, server_key, server_cert, ac_host)

                dest = j.sal.fs.joinPaths(ws.hrd.getStr('service.param.base'), 'cfg/sites-enabled/agentcontroller2')
                if not j.sal.fs.exists(path=dest):
                    j.sal.fs.createDir(j.sal.fs.getParent(dest))
                j.sal.fs.writeFile(filename=dest, contents=cfg)
                ws.restart()