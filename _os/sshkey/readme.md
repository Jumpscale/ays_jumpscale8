

example how to use:

```python
sshkey_palmkey:

#no need to specify a sshkey, because there is only 1 will use that one
host.littlepc.palm_host1:
  rack: 'ourtable'
  addr: '192.168.0.105:22'
```

no need to specify an entry in blueprint about sshkey
this will automatically find the key if the following was in scheme of host.littlepc.palm

```python
sshkeys                        = type:str list consume:sshkey:1
```

this tells that a consumption of an sshkey is a requirement

if key does not exist yet then will generate one

