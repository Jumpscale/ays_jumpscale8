from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    def prepare(self,serviceObj):
        """
        this gets executed before the files are downloaded & installed on appropriate spots
        """
        j.do.execute('apt-get install libqtwebkit4 -y')
        j.do.execute('apt-get install xfce4-terminal -y')

