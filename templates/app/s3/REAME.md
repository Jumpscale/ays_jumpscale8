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
-  hostprefix: the first part in your app url. (i.e hostprefix-machinedecimalip.gigapps.io )
-  fqdn = calculated by ays itself (i.e hostprefix-machinedecimalip.gigapps.io)
-  enablehttps = support for https. `default is False`

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
    hostprefix: 'myapp'
    key.access: '' # optional access key (if empty a new one will be generated)
    key.secret: ''

actions:
  - action: 'install'
```
> NOTE: If `key.access` is not set, a new access key/secret key pair will be generated

> NOTE: Scality doesn't work well with `CyperDuck` the s3 client. To test scality, use `s3cmd`

## `s3cmd` Config
```ini
[default]
access_key = accessKey1
secret_key = verySecretKey1

host_base = mystorage.com
host_bucket = mystorage.com

signature_v2 = True
use_https = False
```
