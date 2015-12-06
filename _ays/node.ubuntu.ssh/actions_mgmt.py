from JumpScale import j




ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


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
        self.enableAccess()
        return True

    def enableAccess(self,serviceObj):
        """
        make sure we can access the environment
        """
        #leave here is to make sure we have a backdoor for when something goes wrong further
        print ("create backdoor")
        cl=self.getCuisine(serviceObj)
        cl.user_ensure("$(system.backdoor.login)", passwd="$(system.backdoor.passwd)", home=None, uid=None, gid=None, shell=None, fullname=None, encrypted_passwd=True, group="root")
        cl.user_passwd("$(system.backdoor.login)", passwd="$(system.backdoor.passwd)", encrypted_passwd=True)

        print ("test backdoor")
        executor=j.tools.executor.getSSHBased(addr="$(node.tcp.addr)", port=port, login="$(system.backdoor.login)", \
                passwd="$(system.backdoor.passwd)", debug=False, checkok=True,allow_agent=False, look_for_keys=False)
        #make sure the backdoor is working
        print ("backdoor is working")

        from IPython import embed
        print ("DEBUG NOW oooioi")
        embed()
        p
        

        print ("make sure some required packages are installed")
        cl.package_ensure('openssl')
        cl.package_ensure('rsync')        

        print ("clean known hosts")
        cl.run("rm -f /root/.ssh/known_hosts")
        print ("add git repos to knownhosts")
        cl.run("ssh-keyscan github.com >> /root/.ssh/known_hosts")
        cl.run("ssh-keyscan git.aydo.com >> /root/.ssh/known_hosts")

        print ("authorize our pub key.")
        # authorize key on node
        pub = serviceObj.hrd.get("ssh.key.public")
        if pub.strip()=="":
            raise RuntimeError("ssh.key.public cannot be empty")
        cl.ssh_authorize("root", pub)
        cl.ssh_authorize("backdoor", pub)
        print ("enable access done.")


    def getCuisine(self,serviceObj):
        """
        @rvalue ssh client object connected to the node
        """

        port = serviceObj.hrd.getInt("ssh.port")
        executor=j.tools.executor.getSSHBased(addr="$(node.tcp.addr)", port=port, login='root', debug=False)
        if e.sshclient.connectTest(die=False):
            #now we will try with passwd as backup
            executor=j.tools.executor.getSSHBased(addr="$(node.tcp.addr)", port=port, login='root', passwd="$(install.seedpasswd)", debug=False, checkok=True)

        return executor.cuisine