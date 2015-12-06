from JumpScale import j
import time

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):
    def prepare(self, serviceObj):
        print("Installing nodejs & npm")
        print("To run nodejs, run /opt/nodejs/bin/node")
        print("To run npm, run /opt/nodejs/bin/npm")
        
    def configure(self, serviceObj):
        j.sal.fs.symlink('/opt/nodejs/lib/node_modules/npm/bin/npm-cli.js','/opt/nodejs/bin/npm',True)
        j.sal.fs.symlink('/opt/nodejs/bin/node','/usr/local/bin/node',True)
        j.sal.fs.symlink('/opt/nodejs/lib/node_modules/npm/bin/npm-cli.js','/usr/local/bin/npm',True)


