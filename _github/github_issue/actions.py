from JumpScale import j


class Actions(ActionsBaseMgmt):

    @action()
    def process(self):       
        repo=self.parent.service.actions.get_github_repo()
        
        from IPython import embed
        print ("DEBUG NOW process")
        embed()
        
        # repo.process_issues()        
    @action()        
    def getIssueFromGithub(self):

        repo=self.service.actions.get_github_repo()

        path=j.sal.fs.joinPaths(self.service.path,"issue.yaml")

        j.sal.fs.writeFile(path,str(md))

