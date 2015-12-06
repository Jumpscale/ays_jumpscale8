from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        prefix = "whoami.git.%s" % "$(git.client.host)"
        data = {
            'host': '$(git.client.host)',
            'login': '$(git.client.login)',
            'passwd': '$(git.client.passwd)'
        }
        hrd = j.data.hrd.get('/opt/jumpscale8/hrd/system/whoami.hrd')
        hrd.set(prefix, data)
        hrd.save()
