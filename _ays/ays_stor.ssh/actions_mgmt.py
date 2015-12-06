from JumpScale import j


ActionsBase = j.atyourservice.getActionsBaseClassMgmt()


class Actions(ActionsBase):

    def consume(self, serviceObj, producer):
        if producer.role == "ays_stor":
            for item in ["root", "tcp.addr"]:
                serviceObj.hrd.set("peer.%s.%s" % (producer.instance, item), producer.hrd.get(item))
