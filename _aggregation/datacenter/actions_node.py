import hashlib
from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):
    def test(self):
        print('TEST FROM NODE')
