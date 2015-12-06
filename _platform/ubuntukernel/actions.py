from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

class Actions(ActionsBase):


    def prepare(self,serviceObj):
        """
        """
        C="""
apt-get install linux-image-generic -f -y
mkdir ~/ovh.d/
sudo mv /etc/grub.d/06_OVHkernel ~/ovh.d
sudo update-grub
sudo apt-get install linux-headers-generic -f -y
"""
        j.do.executeInteractive(C)
        return True

