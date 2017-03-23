# template: node.docker

## Description:

This actor template represents a docker container , it is created through the install action. 
The container is deleted through the uninstall action. 
The container is started through the start action. 
The container is stopped through the stop action. 



## Schema:
 - os: Parent os service name defined in blueprint. *Required*
 - fs: files systems to use on container.
 - docker: docker service to use.
 - hostname: hostname of created conatiner.
 - image: image used to run, default to ubuntu.
 - ports: port forwards to host machine.
 - volumes: files systems to mount on container.
 - cmd: init command to run on container start.
 - sshkey: add ssh key to container.
 - id: id of the container.
 - ip.public: automatically set public ip.
 - ip.private: automatically set private ip.
 - ssh.login: username to login with.
 - ssh.password: password to login with.

## Example:
Replace \<with actual value \>
```yaml
sshkey__ovh_install:

node.physical__ovh4:
  ip.public: '172.17.0.2'
  ssh.login: 'root'
  ssh.password: '<root password>'
  ssh.addr: 'localhost'
  ssh.port: 22

app_docker__appdocker:
  os: ovh4

node.docker__ubuntutest:
  sshkey: 'ovh_install'
  image: 'ubuntu'
  ports:
    - "80:80"
  os: 'ovh4'
  docker: appdocker


actions:
    - action: 'install'
```
