from JumpScale import j


class Actions(ActionsBaseMgmt):

    def input(self,service,recipe,role,instance,args={}):
        if "milestone.title" not in args:
            args['milestone.title']=instance

        return args


    def install(self,service):

        deadline=service.hrd.get("milestone.deadline")

        if deadline.startswith("+"):
            epoch=j.data.time.getEpochFuture(deadline)
            deadline=j.data.time.any2HRDateTime(int(epoch))
        else:
            deadline=j.data.time.any2HRDateTime(deadline)

        service.hrd.set("milestone.deadline",deadline)


        



        