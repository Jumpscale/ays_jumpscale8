## usage of ovc_user
### example
```

g8client__bescale1:
  g8.url: 'be-scale-1.demo.greenitglobe.com'
  g8.login: 'mylogin'
  g8.password: 'secret'
  g8.account: 'cloudpatato01'

# this will check if a user with username 'testuser' exists. if not, it will create it.
ovc_user__user1:
  g8.client.name: 'bescale1'
  username: 'testuser'
  password: 'moehaha' # if not specified, this means that the user will authenticate through itsyou.online
  email: 'user@mail.com' 

vdc__user1:
  g8.client.name: 'bescale1'
  ovc_users:
      - 'user1'
  # Capacity properties are unlimited when filled with -1
  maxMemoryCapacity: 10 # in GB
  maxVDiskCapacity: 100 # in GB
  maxCPUCapacity: 4 # number of cores
  maxNASCapacity: 20 # in TB
  maxArchiveCapacity: 20 # in TB
  maxNetworkOptTransfer: 5 # in GB
  maxNetworkPeerTransfer: 15 # in GB
  maxNumPublicIP: 5 # number of pub ips
```
