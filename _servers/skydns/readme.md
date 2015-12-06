###install
ays install -n skydns --consume 'kv/etcd!member0,kv/etcd!member1'

### TLS
to enable TLS communication between skydns and backend etcd use
```--consume 'tls/cfssl!main'```