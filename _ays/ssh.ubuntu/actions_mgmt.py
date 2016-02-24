import time
from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def hrd(self):
        # sshkey = self._searchDep("sshkey",die=False)
        #
        # if sshkey is not None:
        #     self.service.consume(sshkey)
        # sshkey = j.atyourservice.getService(name='sshkey', instance=self.service.hrd.getStr('sshkey'))

        # self.service.hrd.set("ssh.key.public", producer.hrd.get("key.pub"))
        sshkey = j.atyourservice.getService(role='sshkey', instance=self.service.hrd.getStr('sshkey'))
        self.service.hrd.set("ssh.key.public", sshkey.hrd.get("key.pub"))
        self.service.hrd.set("ssh.key.private", sshkey.hrd.get("key.priv"))

        if self.service.hrd.get("system.backdoor.passwd").strip() == "":
            self.service.hrd.set("system.backdoor.passwd", j.data.idgenerator.generateXCharID(12))
        return True

    #def consume(self, producer):
    #    if producer.role == 'sshkey':
    #        self.service.hrd.set("ssh.key.public", producer.hrd.get("key.pub"))

    def enableAccess(self):
        """
        make sure we can access the environment
        """
        # leave here is to make sure we have a backdoor for when something goes wrong further
        print("create backdoor")
        passwd = self.service.hrd.get("system.backdoor.passwd")
        cl = self._getCuisine()
        self.createbackdoor()
        cl.run("rm -fr /home/$(system.backdoor.login)/.ssh/")

        pub = self.service.hrd.get("ssh.key.public")
        if pub.strip() == "":
            raise RuntimeError("ssh.key.public cannot be empty")

        cl.group.user_add('sudo', '$(system.backdoor.login)')

        print("test backdoor")
        j.tools.executor.getSSHBased(addr="$(node.tcp.addr)", port=int("$(ssh.port)"), login="$(system.backdoor.login)",
                                     passwd=passwd, debug=False, checkok=True, allow_agent=False, look_for_keys=False)
        # make sure the backdoor is working
        print("backdoor is working (with passwd)")  # @todo passwd login is  not working, need to test (*2*)
        cl.ssh.authorize("backdoor", pub)

        print("make sure some required packages are installed")
        # cl.package_ensure_apt('openssl')
        # cl.package_ensure_apt('rsync')

        print("clean known hosts/autorized keys")
        cl.dir_ensure("/root/.ssh")
        cl.dir_remove("/root/.ssh/known_hosts")
        cl.dir_remove("/root/.ssh/authorized_keys")
        print("add git repos to known hosts")
        cl.run("ssh-keyscan github.com >> /root/.ssh/known_hosts")
        cl.run("ssh-keyscan git.aydo.com >> /root/.ssh/known_hosts")

        print("authorize our pub key.")
        # authorize key on node
        cl.ssh.authorize("root", pub)
        print("enable access done.")

    def install_pre(self):
        self.enableAccess()

        if self.service.hrd.getBool('jumpscale.install', default=False):
            self._installJS8(self.service)

    def _installJS8(self, method=None):
        cl = self._getCuisine()
        if method == 'aysfs':
            cl.file_unlink('/usr/local/bin/aysfs')
            cl.file_unlink('/usr/local/bin/js8')
            cl.run("umount -fl /opt;echo")
            cl.run('wget http://stor.jumpscale.org/ays/bin/js8 -O /usr/local/bin/js8')
            cl.file_attribs('/usr/local/bin/js8', mode=774)
            cl.run('/usr/local/bin/js8')
            max = 10
            count = 0
            while not cl.file_exists("/opt/jumpscale8/env.sh") and count < max:
                time.sleep(1)
                count += 1
        else:
            cl.run('cd /tmp;rm -f install.sh;curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh;bash install.sh')

    def _getCuisine(self):
        """
        @rvalue ssh client object connected to the node
        """

        port = int(self.service.hrd.get("ssh.port"))
        executor = j.tools.executor.getSSHBased(addr="$(node.tcp.addr)", port=port, login='root', passwd="$(install.seedpasswd)", debug=False)
        if not executor.sshclient.connectTest(die=False):
            # now we will try with passwd as backup
            executor = j.tools.executor.getSSHBased(addr="$(node.tcp.addr)", port=port, login='root', passwd="$(install.seedpasswd)", debug=False, checkok=True)
            if not executor.sshclient.connectTest(die=False):
                j.events.opserror_critical("can't connect to the node")

        return executor.cuisine

    def createbackdoor(self):
        cl = self._getCuisine()
        print ("creating user", "$(system.backdoor.login)")

        # leave here is to make sure we have a backdoor for when something goes wrong further
        cl.user.ensure("$(system.backdoor.login)", passwd="$(system.backdoor.passwd)", home=None, uid=None, gid=None, shell=None, fullname=None, encrypted_passwd=True, group="root")

    def reset(self):
        # create the backdoor user, make sure is always done, we don't want to be locked out
        self.createbackdoor(self.service)
