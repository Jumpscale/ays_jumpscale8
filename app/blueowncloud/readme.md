# template: blueowncloud

## Description:
This actor is an umbrella service for creating a virtual machine with `Ubuntu 16.04 x64` image with a `btrfs` filesystem.

It creates
  - docker running `tidb` service instance.
  - docker running `owncloud` service instance (with *admin/admin* credentials).


## Schema:

- vdc: cloudspace to create the virtual machine on.
- **optional** ssh: sshkey used to manage the vm.
- datadisks: lists of disk sizes that will be attached to that vm.
- domain: domain name to access the owncloud installation.
> Note: The domain name will just be used for scality configuration and no DNS records will be created. It means that
to access this machine u need either to modify the DNS yourself, or add the `domain` to your `/etc/hosts` file.


## Example blueprint

```yaml

sshkey__demo:

g8client__env1:
    url: 'gig.demo.greenitglobe.com'
    login: 'login'
    password: 'password'
    account: 'account'

vdc__myspaceb15:
    g8client: 'env1'
    location: 'be-conv-2'

blueowncloud__oc1:
    domain: 'mycloud.com'
    vdc: myspaceb15
    datadisks:
        - 1000
        - 1000


```
