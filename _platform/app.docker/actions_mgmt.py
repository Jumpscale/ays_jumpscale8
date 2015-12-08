from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def __init__(self):
        super(Actions, self).__init__()

    def configure(self, serviceObj):
        self.installJS(serviceObj)
        self.installDocker(serviceObj)

    def installJS(self, serviceObj):
        cuisine = self.getCuisine(serviceObj)

        # install js bootstrap
        cuisine.run('wget http://stor.jumpscale.org/ays/bin/js8 -O /usr/local/bin/js8')
        cuisine.file_attribs('/usr/local/bin/js8', mode=774)
        cuisine.run('js8')

    def installDocker(self, serviceObj):
        cuisine = self.getCuisine(serviceObj)

        # install docker
        codename = cuisine.run('lsb_release -sc')
        cuisine.dir_ensure("/etc/apt/sources.list.d")
        source = 'deb https://apt.dockerproject.org/repo ubuntu-%s main' % codename
        cuisine.file_write("/etc/apt/sources.list.d/docker.list", source)
        cuisine.run('apt-get update;apt-cache policy docker-engine; apt-get install -y docker-engine')
        cuisine.run('service docker start')

    def getCuisine(self, serviceObj):
        if serviceObj.parent is None or serviceObj.parent.role != 'os':
            j.events.opserror_critical("can't find parent with role os")
        return serviceObj.parent.actions_mgmt.getCuisine(serviceObj.parent)
