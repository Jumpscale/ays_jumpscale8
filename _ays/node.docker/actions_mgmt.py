from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def consume(self, serviceObj, producer):
        if producer.role == 'sshkey':
            serviceObj.hrd.set('ssh.key.public', producer.hrd.getStr('key.pub'))
