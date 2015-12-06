from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

class Actions(ActionsBase):
    """
    """

    # def prepare(self,serviceObj):
    #     """
    #     this gets executed before the files are downloaded & installed on approprate spots
    #     """        
    #     return True
        
    def configure(self,serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the ays if anything needs to be started
        """        
        serviceObj.hrd.applyOnFile( path="/opt/elasticsearch/config/elasticsearch.yml", additionalArgs={})
        return True

