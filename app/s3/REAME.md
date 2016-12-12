# S3 Umbrella package
S3 is an ays templates that installs an configure a scality s3 machine. 
To create a machine with scality isntalled, follow the example blueprint below.

## Config
```yaml
s3__name:
  vdc: 'vdc-name'
  disk:
    - 'disk1'
  domain: 'hostname.com'
```

- `vdc`: reference the vdc that will have the scality machine
- `disk`: lists of data disks (must be already declared in the blueprint)
- `domain`: a domain name that will be used to access the scality machine.

> Note: The domain name will just be used for scality configuration and no DNS records will be created. It means that
to access this machine u need either to modify the DNS yourself, or add the `domain` to your `/etc/hosts` file.

## Example Blueprint
```yaml
sshkey__demo:

g8client__env1:
    # url: 'du-conv-3.demo.greenitglobe.com'
    url: 'gig.demo.greenitglobe.com'
    login: 'login'
    password: 'password'
    account: 'Acoount'

vdcfarm__vdcfarm1:

vdc__scality:
    vdcfarm: 'vdcfarm1'
    g8client: 'env1'
    # location: 'du-conv-3'
    location: 'be-conv-2'

disk.ovc__disk1:
  size: 1000

s3__demo:
    vdc: 'scality'
    disk:
      - 'disk1'
    domain: 'mystorage.com'

actions:
  - action: 'install'
```

Note: The `sskkey` in the blueprint above is optional. A one will be created for you if it's not specificed in the blueprint.
This `sshkey` is used internally by ays to access the create OVC node (that hosts scality services).