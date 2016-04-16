from JumpScale import j


class Actions():

    def input(self,name,role,instance,args={}):
        if "milestone.title" not in args:
            args['milestone.title']=instance

        return args


    def install(self):

        deadline=self.service.hrd.get("milestone.deadline")

        if deadline.startswith("+"):
            epoch=j.data.time.getEpochFuture(deadline)
            deadline=j.data.time.any2HRDateTime(int(epoch))
        else:
            deadline=j.data.time.any2HRDateTime(deadline)

        self.service.hrd.set("milestone.deadline",deadline)


        



        