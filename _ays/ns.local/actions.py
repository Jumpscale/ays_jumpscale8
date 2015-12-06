from JumpScale import j


ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):


    def register(self,serviceObj,servicename=""):
        domainname="$(ns.domain)"
        fulldns="%s.%s"%(servicename,domainname)
        fulldns=fulldns.replace("..",".")

        c=j.do.readFile("/etc/hosts")

        for line in c.split("\n"):
            if line.strip()=="" or line.startswith("#"):
                continue
            if line.find(fulldns)!=-1:
                continue

        node=serviceObj.getNode()
        if node==None:
            ip="localhost"
        else:
            ip=node.hrd.get("service.ip")

        c=c.strip()
        c+="\n\n%s   %s\n"%(ip,fulldns)
        print(c)
