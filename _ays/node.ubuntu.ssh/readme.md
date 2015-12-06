
## define an ssh key

see
- (ays key ssh info)[https://github.com/Jumpscale/ays_jumpscale8/blob/master/_ays/node.ssh/readme.md]
- make sure you have loaded your sshkeys with ssh-add to remotely access the specified IP addr

## usage of node.ssh

e.g.
```shell
ays init -n node.ssh -i ovh4 --data "ip:94.13.18.89 ssh.port:22"

#there will be automatic ays service consumption for nameserver
#if you want to overrule use following syntax

ays init -n node.ssh -i ovh4 --data "ip:94.13.18.89 ssh.port:22" --consume "ns.local!main"

#consume is in format $role/$domain|$name!$instance,$role2/$domain2|$name2!$instance2

```

```python
data = {
 'ip':"94.13.18.89",
 'ssh.port':22,
 'jumpscale.enable':True,
 'jumpscale.branch':'ays_unstable',
}
ovh = j.atyourservice.new(name='node.ssh',instance="ovh4",args=data)

```

- param: branch is branch of jumpscale which will be installed, only relevant if jumpscale=True

we didn't fill in the password because we are using ssh-agent which is the recommended way
