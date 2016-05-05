
## Example Blueprint

```
datacenter__ovh_germany1:
  location:
    - '...'
  description:
    - '...'

rack__ovh_1:
  location:
    - '...'
  datacenter: 'ovh_germany1'

#make sure we use the ovh_install key we want
# sshkey__ovh_install:
  # key.path: '/root/.ssh/ovh_rsa'

#no need to specify a sshkey, because there is only 1 will use that one
node.physical__ovh4:
  rack: 'ovh_1'
  type: 'develop'
```

- the type is used by e.g. os.ssh to define what needs to be done during install e.g. wipe partitions
- types we are using
    - develop (will wipe partitions during install !!!)
