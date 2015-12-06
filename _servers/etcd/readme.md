
### install stand alone, just leave instance parameters empty.  
```ays install -n etcd -i member0 --data 'cluster.member.names:'' cluster.member.urls:'' cluster.token:''```


### install cluster
install a etcd locally  
```ays install -n etcd -i member0 --data 'cluster.member.names:member0,member1 cluster.member.urls:http://172.20.0.12:2380,http://172.20.0.21:2380 cluster.token:test-cluster'```

install a etcd locally on a remote node.  
```ays install -n etcd -i member1 --data 'cluster.member.names:member0,member1 cluster.member.urls:http://172.20.0.12:2380,http://172.20.0.21:2380 cluster.token:test-cluster listen.client.urls:http://172.20.0.21:2379' --consume 'node/node.ssh!node1'```


- **cluster.member.names**: should be a list of the instance name of the all the services member of the cluster
- **cluster.member.urls**: list of peer listen urls of the etcd cluster members
- **cluster.token**: a unique token for the cluster

### Enable Peer to Peer and client-server authentification
if the etcd service consume a cfssl service with the role TLS,
etcd will be configured to only accept connection if the request provide a certificate that has been signed by the same CA as the one configure in cfssl

in practice, make sure cfssl is installed and has a CA created.
then add ```--consume 'tls/cfssl!main'``` to the install command.