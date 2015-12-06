from JumpScale import j
import signal

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        def createUser():
            if not j.sal.fs.exists(path="/etc/samba/smb.conf"):
                j.sal.fs.createEmptyFile("/etc/samba/smb.conf")
            smb = j.ssh.samba.get(j.ssh.connect())
            smb.addUser('$(ad.username)', '$(ad.passwd)')
        j.actions.start(description='add user to Active directory', action=createUser, category='samba', name='createUser', serviceObj=serviceObj)
