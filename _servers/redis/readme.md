## redis

in memory key value stor with lots of additional features 

### to install locally
```
ays install -n redis -i --data 'param.name:system param.port:7766 param.disk:0  param.mem:100 param.ip:127.0.0.1 param.unixsocket:0 param.passwd:'

```
### to install on remote node example

```
ays init -n node.ssh -i ovh4 --data "ip:94.13.18.89 ssh.port:22"

ays install -n redis -i system --parent '!ovh4' --data 'param.name:system param.port:7766 param.disk:0  param.mem:100 param.ip:127.0.0.1 param.unixsocket:0 param.passwd:'


```