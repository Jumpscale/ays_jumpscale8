## usage for blueprint blueprint.os.ubuntu.openvcloud

### example

```yaml

#ssh key is optional
#sshkey__main:
#    key.name: 'somekey'

g8client__main:
  g8.url: 'be-scale-1.demo.greenitglobe.com'
  g8.login: 'zaibon'
  g8.password: 'secret'

#next is optional, if you want to create your own vdcfarm, if not a 'main' vdcfarm will be created
vdcfarm__myfarm:
  description: 'this is just an aggregation element, can work over multiple G8s'

#next is optional to specify vdc elements
#if account not specified then will be g8.login from g8.client
#if location not specified then the default one will be looked for
vdc__mytest:
  g8.client.name : 'main'
  g8.account : ''
  g8.location : ''

os.ubuntu.openvcloud__mytestmachine:
  #g8.location: ''
  #ssh.key: ''
  #vdc.farm: 'myfarm'
  vdc.name: 'mytest'
  mem.size: 4
  disk.1.size: 100
  disk.2.size: 2000
  disk.3.size: 2000
  


```

- will create on the chosen openvcloud a machine with name mytestmachine in a VDC called mytest
- arguments
    - size of disk is in gb
    - size of mem is in gb 
    - can have upto 10 disks
- this blueprint will
    - sshkey will be fetched if it doesn't exist we will ask for it 
    - account wil be login name if not specified
    - vdc will be created if it does not exist
    - node will be created in vdc with appropriate sizing arguments
    - os will be created inside node and name will be name of instance: mytestmachine in this example
- optional arguments
    - ssh.key name, is name of instance of ssh key, if not specified then will create a new one 
