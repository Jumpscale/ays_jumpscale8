from JumpScale import j




ActionsBase = j.atyourservice.getActionsBaseClassNode()


class Actions(ActionsBase):



    def configure(self, serviceObj):
        self.createbackdoor(serviceObj)

        cl=j.tools.cuisine.local


        # jsbranch = serviceObj.hrd.get('$(jumpscale.branch)')

        cl.run("mkdir -p /etc/ays/local/")

        if  serviceObj.hrd.getBool('jumpscale.install',default=False):
            print("apt-get update & upgrade, can take a while")
            cl.run("apt-get update")
            cl.run("apt-get upgrade -fy")
            cl.package_ensure('curl', update=True)
            cl.package_ensure('tmux', update=True)
            cl.package_ensure('git', update=True)
            # cl.run("apt-get install curl -fy")
            # cl.run("apt-get install tmux -fy")


            cl.fabric.api.env['shell_env']["JSBRANCH"] ='$(jumpscale.branch)'
            cl.fabric.api.env['shell_env']["AYSBRANCH"] = '$(jumpscale.branch)'

            if  serviceObj.hrd.getBool('jumpscale.reset',default=False):
                print("WILL RESET JUMPSCALE")
                cl.run("rm -rf /opt/jumpscale8/hrd/apps")
                # cl.run("cd /opt/code/github/jumpscale/jumpscale_core8;git checkout .")
                # cl.run("cd /opt/code/github/jumpscale/ays_jumpscale8;git checkout .")
                cl.run("rm -rf /opt/code/github/jumpscale/jumpscale_core8")
                cl.run("rm -rf /opt/code/github/jumpscale/ays_jumpscale8")

            elif serviceObj.hrd.getBool('jumpscale.update',default=True):
                cl.run("cd /opt/code/github/jumpscale/jumpscale_core8;git pull origin $(jumpscale.branch)"

            cl.run('git config --global user.name "jumpscale"')
            cl.run('git config --global user.email "jumpscale@fake.com"')

            cl.run("curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/$(jumpscale.branch)/install/install.sh > /tmp/js7.sh && bash /tmp/js7.sh" )

        elif serviceObj.hrd.getBool('jumpscale.update',default=False):
            print("update jumpscale (git)")
            cl.run("cd /opt/code/github/jumpscale/jumpscale_core8;git pull origin %s"%jsbranch)



    def createbackdoor(self,serviceObj):
        #leave here is to make sure we have a backdoor for when something goes wrong further
        j.tools.cuisine.local.user_ensure("$(system.backdoor.login)", passwd="$(system.backdoor.passwd)", home=None, uid=None, gid=None, shell=None, fullname=None, encrypted_passwd=True, group="root")
        j.tools.cuisine.local.user_passwd("$(system.backdoor.login)", passwd="$(system.backdoor.passwd)", encrypted_passwd=True)


    def reset(self, serviceObj):
        #create the backdoor user, make sure is always done, we don't want to be locked out
        self.createbackdoor(serviceObj)