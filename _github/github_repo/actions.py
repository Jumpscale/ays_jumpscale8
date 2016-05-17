from JumpScale import j


class Actions(ActionsBaseMgmt):

    def input(self, name, role, instance, args={}):

        # if repo.name not filled in then same as instance
        if "repo.name" not in args or args["repo.name"].strip() == "":
            args["repo.name"] = instance

        cats = {}
        # check milestone membership
        for aysi in self.service.aysrepo.findServices(role="github_milestone"):
            categories = aysi.hrd.getList("milestone.category")
            for cat in categories:
                if cat not in cats:
                    cats[cat] = []
                if aysi not in cats[cat]:
                    cats[cat].append(aysi)

        if 'milestone.category' in args:

            args["milestones"] = []

            catsToFillIn = args['milestone.category']
            if not j.data.types.list.check(catsToFillIn):
                if catsToFillIn.find(",") != -1:
                    catsToFillIn = [item for item in catsToFillIn.split(",") if item.strip() != ""]
                else:
                    catsToFillIn = [catsToFillIn]

            for catToFillIn in catsToFillIn:
                if catToFillIn in cats:
                    for ays_repo in cats[catToFillIn]:
                        args["milestones"].append(ays_repo.instance)

        if "milestones" in args:
            args["milestones"].sort()

        return args

    @action()
    def init(self):

        # set url based on properties of parent
        url = self.service.parent.hrd.get("github.url").rstrip("/")
        url += "/%s" % self.service.hrd.get("repo.name")
        self.service.hrd.set("repo.url", url)

        # set path based on properties from above

        clienthrd = self.service.producers["github_client"][0].hrd

        clienthrd.set("code.path", j.dirs.replaceTxtDirVars(clienthrd.get("code.path")))

        path = j.sal.fs.joinPaths(clienthrd.get("code.path"), self.service.hrd.get("repo.account"), self.service.hrd.get("repo.name"))

        self.service.hrd.set("code.path", path)

        return True

    def install(self):
        # self.pull()
        self.getIssuesFromGithub()
        self.setMilestonesOnGithub()

    @action()
    def pull(self):
        j.do.pullGitRepo(url=self.service.hrd.get("repo.url"), dest=self.service.hrd.get("code.path"), login=None, passwd=None, depth=1,
                         ignorelocalchanges=False, reset=False, branch=None, revision=None, ssh=True, executor=None, codeDir=None)

    @action()
    def setMilestonesOnGithub(self):

        repo = self.get_github_repo()

        if repo.type in ["proj", "org"]:
            milestonesSet = []
            for service in self.service.getProducers("github_milestone"):
                title = self.service.hrd.get("milestone.title")
                description = self.service.hrd.get("milestone.description")
                deadline = self.service.hrd.get("milestone.deadline")
                owner = self.service.hrd.get("milestone.owner")
                name = self.service.instance

                repo.createMilestone(name, title, description, deadline, owner)

                milestonesSet.append(name)

            # for name in repo.milestoneNames:
            #     if name not in milestonesSet:
            #         repo.deleteMilestone(name)
        # else:
        #     if repo.type not in ["code"]:
        #         for name in repo.milestoneNames:
        #             # repo.deleteMilestone(name)
        #             print("DELETE MILESTONE:%s %s" % (repo, name))

    def getIssuesFromAYS(self):
        githubclientays = self.service.getProducers('github_client')[0]
        client = githubclientays.actions.getGithubClient(service=githubclientays)
        repokey = self.service.hrd.get("repo.account") + "/" + self.service.hrd.get("repo.name")
        repo = client.getRepo(repokey)

        Issue = j.clients.github.getIssueClass()
        for child in self.service.children:
            if child.role != 'github_issue':
                continue
            issue = Issue(repo=repo, ddict=child.model)
            repo.issues.append(issue)

        repo.issues_loaded = True

        return repo

    def get_github_repo(self):
        githubclientays = self.service.getProducers('github_client')[0]
        client = githubclientays.actions.getGithubClient(service=githubclientays)
        repokey = self.service.hrd.get("repo.account") + "/" + self.service.hrd.get("repo.name")
        repo = client.getRepo(repokey)
        fromAys = True
        if self.service.state.get("getIssuesFromGithub")[0] != "OK":
            # means have not been able to get the issues from github properly, so do again
            fromAys = False
        if not repo.issues_loaded:
            if fromAys:
                print("LOAD ISSUES FROM AYS")
                # self.service.state.set("getIssuesFromAYS","DO")
                self.getIssuesFromAYS()
                repo.issues_loaded = True
            else:
                from IPython import embed
                print("DEBUG NOW issues loaded false,LOAD ISSUES FROM GITHUB")
                embed()
                ppp
                print("LOAD ISSUES FROM GITHUB")
                # self.service.state.set("getIssuesFromGithub","DO")
                self.getIssuesFromGithub(service=service)
                repo.issues_loaded = True
        return repo

    @action()
    def processIssues(self):
        repo = self.get_github_repo(service)
        repo.process_issues()

    def stories2pdf(self):
        repo = self.get_github_repo(service)
        from IPython import embed
        print("DEBUG NOW stories 2 pdf")
        embed()

    @action()
    def test(self):
        print("TEST")

    @action()
    def getIssuesFromGithub(self):
        config = self.service.getProducers('github_config')[0]

        projtype = self.service.hrd.get("repo.type")
        labels = []

        for key, value in config.hrd.getDictFromPrefix("github.label").items():
            # label=key.split(".")[-1]
            label = key.replace(".", "_")
            if projtype in value or "*" in value:
                labels.append(label)

        githubclientays = self.service.getProducers('github_client')[0]
        client = githubclientays.actions.getGithubClient(service=githubclientays)

        reponame = "$(repo.account)/$(repo.name)"
        r = client.getRepo(reponame)

        # first make sure issues get right labels
        r.labelsSet(labels, ignoreDelete=["p_"])

        labelsprint = ",".join(labels)

        self.service.logger.info("Have set labels in %s:%s" % (service, labelsprint))

        issues = r.loadIssues()

        if issues != []:
            for issue in issues:
                args = {'github.repo': self.service.instance}
                issue_service = self.service.aysrepo.new(name='github_issue', instance=str(issue.id), args=args, model=issue.ddict)

        self.service.state.set("getIssuesFromGithub", "OK")
        self.service.state.save()

        r.issues_loaded = True

        self.processIssues()
