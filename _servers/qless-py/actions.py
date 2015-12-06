from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

class Actions(ActionsBase):

    def init(self,serviceObj):
        instance=serviceObj.hrd.get("param.redis.instance")
        
        jpredis=j.packages.get(name="redis",instance=instance,node=serviceObj.node)
        serviceObj.hrd.set("param.redis.host","localhost")
        serviceObj.hrd.set("param.redis.port", jpredis.hrd.get("param.port"))
        return True

    def configure(self,serviceObj):
        j.sal.fs.changeDir("$(system.paths.base)/apps/qless-core/")
        j.do.execute("make qless.lua")
