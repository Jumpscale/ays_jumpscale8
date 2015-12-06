from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        if 'kv' not in serviceObj.producers:
            j.events.inputerror_critical(msg="This service need to consume an etcd service with the role 'kv'", category="skydns_configure")

        etcds = serviceObj.producers['kv']
        listen_addr = serviceObj.hrd.getStr('listen.addr')
        domain = serviceObj.hrd.getStr('domain')

        machines = ""
        for etcd_service in etcds:
            urls = etcd_service.hrd.getStr('listen.client.urls')
            machines += '%s,' % urls
        machines = machines.rstrip(",")

        # update process definition
        proc = serviceObj.hrd.getDictFromPrefix('service.process')['1']
        proc['args'] = '-domain %s -addr %s' % (domain, listen_addr)
        proc['args'] += ' -machines %s' % machines

        serviceObj.hrd.set('service.process.1', proc)
        serviceObj.hrd.save()

        # TLS configuration
        if 'tls' in serviceObj.producers:
            cfssl_service = serviceObj.producers['tls'][0]
            tls = cfssl_service.actions.getTLS()
            name = "skydns-%s" %
            subjects = [{
                "C": "AE",
                "L": "Dubai",
                "O": "GreenITGlobe",
                "OU": "0-complexity",
                "ST": "Dubai",
                "CN": name
            }]

            hosts = ['localhost']
            ca = cfssl_service.hrd.get('ca.cert')
            ca_key = cfssl_service.hrd.get('ca.key')
            cert, key = tls.createSignedCertificate(name, subjects, hosts, ca, ca_key)

            # server to server authentification
            proc['args'] += ' -tls-pem %s -tls-key %s -ca-cert %s' % (cert, key, ca)
            serviceObj.hrd.set('service.process.1', proc)
            serviceObj.hrd.save()
