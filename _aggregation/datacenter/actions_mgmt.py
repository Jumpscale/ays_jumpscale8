import hashlib
from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def install_pre(self):

        print("we would do some capacity planning action to reality db")

    def install_post(self):

        print("send email to customer")

    def test(self):
        print('TEST FROM MGMT')
