from JumpScale import j
import JumpScale.sal.kvm

ActionsBase = j.atyourservice.getActionsBaseClassNode()


class Actions(ActionsBase):

    def prepare(self, serviceObj):
        # install required packages
        packages = 'qemu-kvm qemu python-libvirt virt-viewer libvirt-bin bridge-utils'
        j.sal.ubuntu.apt_install(packages)


    def install(self,serviceObj):
        # download images
        ftp = j.clients.ftp.get('ftp.aydo.com', 'pub', 'pub1234')
        ftp.download('Linux/ubuntu/Ubuntu.15.10.x64.qcow2', '/mnt/vmstor/kvm/images/Ubuntu.15.10.x64.qcow2')

        # create bridge
        j.sal.nettools.setBasicNetConfigurationBridgePub()
        j.sal.kvm.initPhysicalBridges()
