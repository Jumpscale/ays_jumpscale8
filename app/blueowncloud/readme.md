# template: blueowncloud

## Description:
This actor is an umbrella service for creating a virtual machine with `g8os-test-1604` image with a `btrfs` filesystem.

It creates
  - docker running `tidb` service instance.
  - docker running `owncloud` service instance (with *admin/admin* credentials).


## Schema:

- **optional** vdc: cloudspace to create the virtual machine on.
- **optional** ssh: sshkey used to manage the vm.
- datadisks: lists of disk sizes that will be attached to that vm.
- domain: site name for generating configurations for nginx.
