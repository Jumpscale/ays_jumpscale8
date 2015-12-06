
## docker ays on top of ssh node

```python

data = {
    'node.tcp.addr':'94.23.38.89',
    'jumpscale.enable':False
}
host = j.atyourservice.new(name='node.ssh',instance="ovh4",args=data)

data = {
 'docker.image':'jumpscale/ubuntu:15.04',
 'docker.portsforwards':"80:8080",
 'docker.volumes':"/tmp:/tmp",
 'jumpscale.enable':True,
 'jumpscale.branch':'ays_unstable',
}

nodedocker = j.atyourservice.new(name='node.docker',instance="ourmaster",args=data,parent=host)

j.atyourservice.apply()

```

- param: branch is branch of jumpscale which will be installed, only relevant if jumpscale=True