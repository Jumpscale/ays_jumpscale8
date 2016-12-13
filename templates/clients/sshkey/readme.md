# Template: sshkey
Used to manage your remote ays services through  by `consuming existing ones` or `generating new ones.`

## Schema
```
key.path = type:str
key.name = type:str
key.passphrase= type:str default:'' descr:'Specify passphrase (default is empty)'
key.priv = type:str
key.pub = type:str
```
where:
- `key.path`: is the path of an existing key to be used.
- `key.name`: sshkey name (can be used to get the path of the sshkey by its name).
- `key.passphrase`: sshkey passphrase.
- `key.priv`: private sshkey.
- `key.pub`: public sshkey.


## Example blueprint
```yaml
sshkey__demo:


g8client__env1:
    # url: 'du-conv-3.demo.greenitglobe.com'
    url: 'gig.demo.greenitglobe.com'
    login: 'login'
    password: 'password'
    account: 'account'

disk.ovc__disk1:
  size: 1000
  type: 'D'

uservdc__thabeta:
  g8client: env1

vdc__v2:
  uservdc:
    - thabeta
  location: 'be-conv-2'
  g8client: env1

node.ovc__n1:
  os.image: "Ubuntu 16.04 x64"
  disk:
    - disk1
  vdc: v2
  ports:
        - '22'
        - '80:80'
        - '443:443'

```
