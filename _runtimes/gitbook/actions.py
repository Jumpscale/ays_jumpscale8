from JumpScale import j
import time

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):
    def prepare(self, serviceObj):
        print("INSTALL GITBOOK BY MEANS OF NPM (THIS CAN TAKE A WHILE)")
        j.do.executeInteractive("npm install -g gitbook")
        # url="https://github.com/MrMaksimize/gitbook-starter-kit.git"

    def configure(self, serviceObj):
        pass

