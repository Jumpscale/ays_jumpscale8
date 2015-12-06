from JumpScale import j




ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def consume(self, serviceObj, producer):
        if producer.role == 'ays_stor':
            serviceObj.hrd.set('key.read', producer.hrd.getStr('read.key'))
            serviceObj.hrd.set('key.write', producer.hrd.getStr('write.key'))
            # serviceObj.hrd.set('ip.%s' % producer.instance, producer.hrd.getStr('tcp.addr'))
            serviceObj.hrd.set('root', producer.hrd.getStr('root'))
