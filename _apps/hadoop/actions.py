from JumpScale import j


class Actions(ActionsBaseMgmt):
    def install(self, service):
        service.executor.cuisine.apps.hadoop.build()
