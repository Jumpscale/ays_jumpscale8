from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassNode()


class Actions(ActionsBase):

    def prepare(self, serviceObj):
        """
        download required docker images
        """
        j.sal.docker.images.pull("jumpscale/pxeboot")

    def configure(self, serviceObj):
        executor = j.tools.executor.getLocal()
        # download images/installer...
        conn.execute("wget http://stor.jumpscale.org:8000/images/pxe.tgz -O /root/pxe.tgz")
        executor.execute("cd /root; tar -xvf /root/pxe.tgz")

        container = j.sal.docker.create("pxeboot", vols='/root/tftpboot:/data/tftpboot#/root/conf:/data/conf', base='jumpscale/pxeboot')
