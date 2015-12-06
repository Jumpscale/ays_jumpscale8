
## define an ssh key

see
- (ays key ssh info)[https://github.com/Jumpscale/ays_jumpscale8/blob/master/_ays/node.ssh/readme.md]

## usage of node.ssh

e.g.
```
ays install -n sshkey -i dubai_key
```

```
data = {
 'ip':"94.13.18.89",
 'ssh.port':22,
 'login':'root',
 'password':'',
 'jumpscale':False,
 'branch':'master',
}
ovh = j.atyourservice.new(name='node.ssh',instance="ovh4",args=data)
ovh.consume("sshkey:dubai_key","sshkey")
ovh.install()

```

- param: branch is branch of jumpscale which will be installed, only relevant if jumpscale=True

we didn't fill in the password because we are using ssh-agent which is the recommended way
