# template: vfs

## Description:
This actor template is responsible to install and managed the [G8OS virtual filesystem](https://github.com/g8os/fs)

This template has the informations about a list of flist it should start after installation. See the detail about the flist definition format down below

## Schema:

- os: service name of the os.ssh parent from this template. **required**

## Actor.hrd:
This service can define a list of flist in it's actor.hrd file.
Format to defnine a flits is the following:
```hrd
flists.global =
    namespace: 'ns1',
    mountpoint: '/path/to/mountpoint',
    mode:  'ro',
    store_url: 'http://mystore.com',

flists.extra =
    namespace: 'ns2',
    mountpoint: '/path/to/mountpoint',
    mode:  'rw',
    store_url: 'http://mystore.com',
```

- namespace : is the namespace in the store where the binary file have been pushed to
- mountpoint: is where the fuse filesystem will create it's mountpoint
- mode: mode of the filesystem, it can be:
 - ro: read-only
 - rw: read-write
 - ol: overlay mode
- store_url: full URL of the store you want to use for that flist.
