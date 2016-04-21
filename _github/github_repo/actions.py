from JumpScale import j


class Actions():


    def input(self,name,role,instance,args={}):

        #if repo.name not filled in then same as instance
        if "repo.name" not in args or args["repo.name"].strip()=="":
            args["repo.name"]=instance

        cats={}
        #check milestone membership
        for aysi in j.atyourservice.findServices(role="github_milestone"):
            categories=aysi.hrd.getList("milestone.category")
            for cat in categories:
                if cat not in cats:
                    cats[cat]=[]
                if aysi not in cats[cat]:
                    cats[cat].append(aysi)


        if 'milestone.category' in args:

            args["milestones"]=[]

            catsToFillIn=args['milestone.category']
            if not j.data.types.list.check(catsToFillIn):
                if catsToFillIn.find(",")!=-1:
                    catsToFillIn=[item for item in catsToFillIn.split(",") if item.strip()!=""]
                else:
                    catsToFillIn=[catsToFillIn]

            for catToFillIn in catsToFillIn:
                if catToFillIn in cats:
                    for ays_repo in cats[catToFillIn]:
                        args["milestones"].append(ays_repo.instance)        

        args["milestones"].sort()

        return args

    def init(self):

        #set url based on properties of parent
        url=self.service.parent.hrd.get("github.url").rstrip("/")
        url+="/%s"%self.service.hrd.get("repo.name")
        self.service.hrd.set("repo.url",url)

        #set path based on properties from above

        clienthrd=self.service.producers["github_client"][0].hrd

        clienthrd.set("code.path",j.dirs.replaceTxtDirVars(clienthrd.get("code.path")))

        path=j.sal.fs.joinPaths(clienthrd.get("code.path"),self.service.hrd.get("repo.account"),self.service.hrd.get("repo.name"))

        self.service.hrd.set("code.path",path)
        
        return True

    def install(self):
        self.service.actions.pull(force=True)
        self.service.actions.getIssuesFromGithub(force=True)
        self.service.actions.setMilestonesOnGithub(force=True)

    def action_pull(self):
        j.do.pullGitRepo(url=self.service.hrd.get("repo.url"), dest= self.service.hrd.get("code.path"), login=None, passwd=None, depth=1, \
            ignorelocalchanges=False, reset=False, branch=None, revision=None, ssh=True, executor=None, codeDir=None)


    def action_setMilestonesOnGithub(self):

        repo=self.service.actions.get_github_repo()

        if repo.type in ["proj","org"]:            
            milestonesSet=[]
            for service in self.service.getProducers("github_milestone"):
                title=service.hrd.get("milestone.title")
                description=service.hrd.get("milestone.description")
                deadline=service.hrd.get("milestone.deadline")
                owner=service.hrd.get("milestone.owner")
                name=service.instance

                repo.createMilestone(name,title,description,deadline,owner)

                milestonesSet.append(name)

            for name in repo.milestoneNames:
                if name not in milestonesSet:
                    repo.deleteMilestone(name)
        else:
            if repo.type not in ["code"]:
                for name in repo.milestoneNames:
                    # repo.deleteMilestone(name)
                    print ("DELETE MILESTONE:%s %s"%(repo,name))


    def getIssuesFromAYS(self):

        repo=self.service.actions.get_github_repo()

        path=j.sal.fs.joinPaths(self.service.path,"issues.md")
        content=j.sal.fs.fileGetContents(path)

        md=j.data.markdown.getDocument(content)    

        issueblock=""        
        state="start"
        issueNumber=0
        for item in md.items:
            print(item.type)

            if item.type=="comment1line": 
                if issueNumber!=0:
                    #process previously gathered issue
                    issue=repo.getIssueFromMarkdown(issueNumber,issueblock)

                issueblock=""
                state="block"
                issueNumber=j.data.tags.getObject(item.text).tagGet("issue")                   
                continue

            if state=="block":
                issueblock+=str(item)+"\n"   

        if issueNumber!=0:
            repo.getIssueFromMarkdown(issueNumber,issueblock)

        from IPython import embed
        print ("DEBUG NOW get issues from repo")
        embed()
        

        return repo
        
    def get_github_repo(self):
        client=self.service.getProducers('github_client')[0].actions.getGithubClient()
        return client.getRepo("$(repo.account)/$(repo.name)")

    def action_processIssues(self):
        # repo=self.service.actions.getIssuesFromAYS()
        repo=self.service.actions.get_github_repo()
        if repo.issues==[]:
            self.service.state.set("getIssuesFromGithub","WAIT")
            self.service.actions.getIssuesFromGithub()   
            repo=self.service.actions.get_github_repo()

        repo.process_issues()
        
    def action_getIssuesFromGithub(self):
        config=self.service.getProducers('github_config')[0]

        projtype=self.service.hrd.get("repo.type")
        labels=[]

        for key, value in config.hrd.getDictFromPrefix("github.label").items():
            # label=key.split(".")[-1]
            label=key.replace(".","_")
            if projtype in value or "*" in value:
                labels.append(label)   


        client=self.service.getProducers('github_client')[0].actions.getGithubClient()

        r=client.getRepo("$(repo.account)/$(repo.name)")

        #first make sure issues get right labels
        r.labels=labels

        print ("Have set labels in %s:\n***\n%s\n***\n"%(self.service,labels))
        # from pudb import set_trace; set_trace() 

        issues=r.loadIssues()

        md=j.data.markdown.getDocument()
        md.addMDHeader(1, "Issues")

        res=r.issues_by_type_state()

        for type in r.types:
            typeheader=False            
            for state in r.states:
                issues=res[type][state]
                stateheader=False
                for issue in issues:
                    if typeheader==False:
                        md.addMDHeader(2, "Type:%s"%type)
                        typeheader=True
                    if stateheader==False:
                        md.addMDHeader(3, "State:%s"%state)
                        stateheader=True
                    md.addMDBlock(str(issue.getMarkdown()))

        path=j.sal.fs.joinPaths(self.service.path,"issues.md")

        j.sal.fs.writeFile(path,str(md))

        self.service.actions.processIssues(force=True)



    def change(self,stateitem):
        if stateitem.name not in ["install"]:
            stateitemToChange=self.service.state.getSet("install")
            if stateitemToChange.state=="OK":
                stateitemToChange.state="CHANGED"
                self.service.state.save()



        