from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def hrd(self, serviceObj, producer):
        depkey =
        energyswitch = self._searchDep(serviceObj, "sshkey",die=False)
        if energyswitch!=None:
            serviceObj.consume(energyswitch)

    def consume(self, serviceObj, producer):
        if producer.role == 'sshkey':
            # serviceObj.consume(serv)
            serviceObj.hrd.set("ssh.key.public", producer.hrd.get("key.pub"))

    def hrd(self, serviceObj):
        if serviceObj.hrd.get("system.backdoor.passwd").strip()=="":
            serviceObj.hrd.set("system.backdoor.passwd",j.tools.idgenerator.generateXCharID(12))
        self.enableAccess(serviceObj)
        return True

    def enableAccess(self,serviceObj):
        """
        make sure we can access the environment
        """
        #leave here is to make sure we have a backdoor for when something goes wrong further
        print("create backdoor")
        passwd=serviceObj.hrd.get("system.backdoor.passwd")
        cl=self._getCuisine(serviceObj)
        self.createbackdoor(serviceObj)
        cl.run("rm -fr /home/$(system.backdoor.login)/.ssh/")

        pub = serviceObj.hrd.get("ssh.key.public")
        if pub.strip()=="":
            raise RuntimeError("ssh.key.public cannot be empty")

        cl.group_user_add('sudo', '$(system.backdoor.login)')

        print("test backdoor")
        executor=j.tools.executor.getSSHBased(addr="$(node.tcp.addr)", port="$(ssh.port)", login="$(system.backdoor.login)", \
                passwd=passwd, debug=False, checkok=True,allow_agent=False, look_for_keys=False)
        #make sure the backdoor is working
        print("backdoor is working (with passwd)")  #@todo passwd login is  not working, need to test (*1*)
        cl.ssh_authorize("backdoor", pub)

        print("make sure some required packages are installed")
        # cl.package_ensure_apt('openssl')
        # cl.package_ensure_apt('rsync')

        print("clean known hosts/autorized keys")
        cl.dir_remove("/root/.ssh/known_hosts")
        cl.dir_remove("/root/.ssh/authorized_keys")
        print("add git repos to known hosts")
        cl.run("ssh-keyscan github.com >> /root/.ssh/known_hosts")
        cl.run("ssh-keyscan git.aydo.com >> /root/.ssh/known_hosts")

        print("authorize our pub key.")
        # authorize key on node
        cl.ssh_authorize("root", pub)
        print("enable access done.")

    def _getCuisine(self,serviceObj):
        """
        @rvalue ssh client object connected to the node
        """
        port = serviceObj.hrd.getInt("ssh.port")
        executor=j.tools.executor.getSSHBased(addr="$(node.tcp.addr)", port=port, login='root', debug=False)
        if not executor.sshclient.connectTest(die=False):
            #now we will try with passwd as backup
            executor=j.tools.executor.getSSHBased(addr="$(node.tcp.addr)", port=port, login='root', passwd="$(install.seedpasswd)", debug=False, checkok=True)
            if not executor.sshclient.connectTest(die=False):
                j.events.opserror_critical("can't connect to the node")

        return executor.cuisine

    def createbackdoor(self,serviceObj):
        cl=self._getCuisine(serviceObj)
        #leave here is to make sure we have a backdoor for when something goes wrong further
        cl.user_ensure("$(system.backdoor.login)", passwd="$(system.backdoor.passwd)", home=None, uid=None, gid=None, shell=None, fullname=None, encrypted_passwd=True, group="root")
        cl.user_passwd("$(system.backdoor.login)", passwd="$(system.backdoor.passwd)", encrypted_passwd=True)

    def reset(self, serviceObj):
        #create the backdoor user, make sure is always done, we don't want to be locked out
        self.createbackdoor(serviceObj)
