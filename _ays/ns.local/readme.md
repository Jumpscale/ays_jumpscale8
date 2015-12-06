
## ns.local

this ays is the root of all services
it stands for the nameserver
use this service if you want to use the local host file as nameserver

there is also a ns.aydo which registers to the aydo nameservers which can be used by our customers (PLEASE DO NOT ABUSE)

e.g.
```
ays install -n ns.local -i main --data "ns.domain:mydomain.com"
```

```
data = {
 'ns.domain':"mydomain.com",
}
ns = j.atyourservice.new(name='ns.local',instance="main",args=data)

```

