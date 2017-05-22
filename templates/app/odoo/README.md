# template: odoo

## Description:

This actor template creates an odoo instance running on the specified node with the basic accounting configurations and instance specific params: company_name, admin username, admin password.
These params are specified per instance. The server uses [ERPpeek](https://pypi.python.org/pypi/ERPpeek) python library to create and manipulate the database through XML-RPC calls.

## Schema:
 - os : type:string os service name , required.
 - company : type:string company name, required.
 - username : type:string admin username, required.
 - password : type:string admin password, required.

## Example:

```yaml 
sshkey__main:

node.physical__demo:
  ip.public: '192.168.21.113'
  ssh.login: 'root'
  ssh.password: 'gig1234'
  ssh.addr: '192.168.21.113'
  ssh.port: 22
  sshkey: main

node.docker__OdooContainer:
  image: 'jumpscale/ubuntu1604'
  hostname: demo
  os: demo
  ports: 
    - "8069:8069"
    - "2210:22"
odoo__main:
  company: 'CodeScalars'
  username: 'root'
  password: 'rooter'
  os: OdooContainer

actions:
  - action: 'install'
```
