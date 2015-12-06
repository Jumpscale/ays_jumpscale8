from JumpScale import j




ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def consume(self, serviceObj, producer):
        pass
        # if producer.role == 'ays_stor':
        #     serviceObj.hrd.set('key.read' % producer.instance, producer.hrd.getStr('read.key'))
        #     serviceObj.hrd.set('key.write' % producer.instance, producer.hrd.getStr('write.key'))
        #     # serviceObj.hrd.set('ip.%s' % producer.instance, producer.hrd.getStr('tcp.addr'))
        #     serviceObj.hrd.set('root' % producer.instance, producer.hrd.getStr('root'))
