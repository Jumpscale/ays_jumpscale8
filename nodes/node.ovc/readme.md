# template: node.ovc

## Description:
This actor template is responsible to create a virtual machine on any openVCloud environment.

## Schema:

- description: arbitratry description of the vm. **optional**
- bootdisk.size: boot disk size in GB default:10. **required**
- datadisks: list of extra data disks size in GB. **optional**
- os.size: Type of VM, this size impact the number of CPU and memory available for the vm. **required**
- os.image: OS image to use for the VM. **required**
- ports: List of port forward to create. Format is `Public_port:VM_port` or `VM_port`.
if the public port is not specified, it will be choose automaticlly in the available port of the vdc.  
e.g: to expose port 22 of the VM to the port 9000 on the public port of the vdc use :`9000:22`. **optional**

- machine.id: once the VM is created, holds the ID return by openvcloud for that VM. **fill automaticlly, don't specify it in Blueprint**
- ip.public: public IP of the VM once installed. **fill automaticlly, don't specify it in Blueprint**
- ip.private: private IP of the VM inside the VDC. **fill automaticlly, don't specify it in Blueprint**

- ssh.login: login used to create ssh connection to the VM. **fill automaticlly, don't specify it in Blueprint**
- ssh.password: password used to create ssh connection to the vm. **fill automaticlly, don't specify it in Blueprint**

- vdc: service name of the vdc service where to deploy the VM. This is the parent service. **required**
