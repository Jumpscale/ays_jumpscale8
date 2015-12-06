from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        member_names = serviceObj.hrd.getList('cluster.member.names')
        member_urls = serviceObj.hrd.getList('cluster.member.urls')

        if len(member_names) != len(member_urls):
            j.events.inputerror_critical(msg="number of member names should be egal to number of member urls", category="etcd_configure")

        cluster = {}
        initial_cluster = ""
        for i in range(len(member_urls)):
            initial_cluster += "%s=%s," % (member_names[i], member_urls[i])
            cluster[member_names[i]] = member_urls[i]
        initial_cluster = initial_cluster.rstrip(",")

        # update process definition
        proc = serviceObj.hrd.getDictFromPrefix('service.process')['1']
        proc['args'] = '-name $(service.instance) -data-dir $(system.paths.var)/etcd/$(service.instance) -listen-client-urls $(listen.client.urls) -advertise-client-urls $(listen.client.urls)'
        if len(member_names) > 0:
            proc['args'] += ' -initial-advertise-peer-urls %s -listen-peer-urls %s ' % (cluster[], cluster[])
            proc['args'] += ' -initial-cluster %s -initial-cluster-state new' % initial_cluster
        serviceObj.hrd.set('service.process.1', proc)
        serviceObj.hrd.save()

        # TLS configuration
        if 'tls' in serviceObj.producers and len(member_names) > 0:
            cfssl_service = serviceObj.producers['tls'][0]
            tls = cfssl_service.actions.getTLS()
            name = "etcd-%s" % 
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
            proc['args'] += ' --peer-client-cert-auth --peer-cert-file %s --peer-key-file %s --peer-trusted-ca-file %s' % (cert, key, ca)
            # client to server authentification
            proc['args'] += ' --client-cert-auth --cert-file %s --key-file %s --trusted-ca-file %s' % (cert, key, ca)
            serviceObj.hrd.set('service.process.1', proc)
            serviceObj.hrd.save()