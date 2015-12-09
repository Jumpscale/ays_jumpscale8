from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassNode()


class Actions(ActionsBase):

    def install(self, serviceObj):
        super(Actions, self).install(serviceObj)
        self.installDocker(serviceObj)

    def installDocker(self, serviceObj):
        cuisine = j.tools.cuisine.local
        # install docker
        cuisine.run('apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D')
        codename = cuisine.run('lsb_release -sc')
        cuisine.dir_ensure("/etc/apt/sources.list.d")
        source = 'deb https://apt.dockerproject.org/repo ubuntu-%s main' % codename
        cuisine.file_write("/etc/apt/sources.list.d/docker.list", source)
        cuisine.run('apt-get update;apt-cache policy docker-engine; apt-get install -y docker-engine')
        cuisine.run('service docker start')
