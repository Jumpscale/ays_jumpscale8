from JumpScale import j




ActionsBase = j.atyourservice.getActionsBaseClassNode()


class Actions(ActionsBase):

    def init(self, serviceObj, args):
        """
        will install a node over ssh
        """
        ActionsBase.init(self, serviceObj, args)

        depkey = "sshkey"

        if serviceObj.originator is not None and serviceObj.originator._producers != {} and depkey in serviceObj.originator._producers:
            res = serviceObj.originator._producers[depkey]
        elif serviceObj._producers!={} and depkey in serviceObj._producers:
            res = serviceObj._producers[depkey]
        else:
            # we need to check if there is a specific consumption specified, if not check generic one
            res = j.atyourservice.findServices(role=depkey)

        if len(res) == 0:
            # not deployed yet
            j.events.inputerror_critical("Could not find dependency, please install.\nI am %s, I am trying to depend on %s" % (serviceObj, depkey))
        elif len(res) > 1:
            j.events.inputerror_critical("Found more than 1 dependent ays, please specify, cannot fullfil dependency requirement.\nI am %s, I am trying to depend on %s" % (serviceObj, depkey))
        else:
            serv = res[0]

        serviceObj.consume(serv)

        args["ssh.key.public"] = serv.hrd.get("key.pub")

    def configure(self, serviceObj):


        # authorize key on node
        cl = self.getSSHClient(serviceObj)
        pub = serviceObj.hrd.get("ssh.key.public")
        if pub:
            login = serviceObj.hrd.get('login',default="")
            if login.strip() == '':
                login = 'root'
            cl.ssh_authorize(login, pub)


        cl.run("rm -f /root/.ssh/known_hosts")
        cl.run("ssh-keyscan github.com >> /root/.ssh/known_hosts")
        cl.run("ssh-keyscan git.aydo.com >> /root/.ssh/known_hosts")  
        
        jsbranch = serviceObj.hrd.get('jumpscale.branch')  

        print("apt-get update & upgrade, can take a while")
        cl.run("apt-get update")
        cl.run("apt-get upgrade -f")
        cl.run("apt-get install curl -f")
        cl.run("apt-get install tmux -f")     
        cl.run("mkdir -p /etc/ays/local/")       

        if  serviceObj.hrd.getBool('jumpscale.install',default=False):

            # cl.package_ensure('curl', update=True)
            # cl.package_ensure('tmux', update=True)

            cl.fabric.api.env['shell_env']["JSBRANCH"] =jsbranch
            cl.fabric.api.env['shell_env']["AYSBRANCH"] = serviceObj.hrd.get('jumpscale.branch')

            if  serviceObj.hrd.getBool('jumpscale.reset',default=False):
                print("WILL RESET JUMPSCALE")
                cl.run("rm -rf /opt/jumpscale8/hrd/apps")
                # cl.run("cd /opt/code/github/jumpscale/jumpscale_core8;git checkout .")
                # cl.run("cd /opt/code/github/jumpscale/ays_jumpscale8;git checkout .")
                cl.run("rm -rf /opt/code/github/jumpscale/jumpscale_core8")
                cl.run("rm -rf /opt/code/github/jumpscale/ays_jumpscale8")
                
            elif serviceObj.hrd.getBool('jumpscale.update',default=True):
                cl.run("cd /opt/code/github/jumpscale/jumpscale_core8;git pull origin %s"%jsbranch)

            cl.run('git config --global user.name "jumpscale"')
            cl.run('git config --global user.email "jumpscale@fake.com"')

            cl.run("curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/%s/install/install.sh > /tmp/js7.sh && bash /tmp/js7.sh" % jsbranch)

        elif serviceObj.hrd.getBool('jumpscale.update',default=False):
            print("update jumpscale (git)")
            cl.run("cd /opt/code/github/jumpscale/jumpscale_core8;git pull origin %s"%jsbranch)


        return True


    def getSSHClient(self,serviceObj):
        """
        @rvalue ssh client object connected to the node
        """
        ip=serviceObj.hrd.get("node.tcp.addr")
        port=serviceObj.hrd.getInt("ssh.port")
        login='root'
        password=""

        c = j.remote.cuisine
        c.fabric.env['forward_agent'] = True

        if login and login.strip() != '':
            c.fabric.env['user'] = login

        if password and password.strip() != '':
            connection = c.connect(ip, port, passwd=password)
        else:
            connection = c.connect(ip, port)

        return connection



