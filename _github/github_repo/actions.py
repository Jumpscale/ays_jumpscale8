from JumpScale import j


class Actions(ActionsBaseMgmt):

    def input(self, service, name, role, instance, args={}):

        # if repo.name not filled in then same as instance
        if "repo.name" not in args or args["repo.name"].strip() == "":
            args["repo.name"] = instance

        cats = {}
        # check milestone membership
        for aysi in service.aysrepo.findServices(role="github_milestone"):
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
    def init(self, service):

        # set url based on properties of parent
        url = service.parent.hrd.get("github.url").rstrip("/")
        url += "/%s" % service.hrd.get("repo.name")
        service.hrd.set("repo.url", url)

        # set path based on properties from above

        clienthrd = service.producers["github_client"][0].hrd

        clienthrd.set("code.path", j.dirs.replaceTxtDirVars(clienthrd.get("code.path")))

        path = j.sal.fs.joinPaths(clienthrd.get("code.path"), service.hrd.get("repo.account"), service.hrd.get("repo.name"))

        service.hrd.set("code.path", path)

        return True

    def install(self, service):
        self.setMilestonesOnGithub(service=service)
        self.processIssues(service=service, refresh=True)

    @action()
    def pull(self, service):
        j.do.pullGitRepo(url=service.hrd.get("repo.url"), dest=service.hrd.get("code.path"), login=None, passwd=None, depth=1,
                         ignorelocalchanges=False, reset=False, branch=None, revision=None, ssh=True, executor=None, codeDir=None)

    @action()
    def setMilestonesOnGithub(self, service):
        repo = self.get_github_repo(service=service)

        if repo.type in ["proj", "org"]:
            milestonesSet = []
            for service in service.getProducers("github_milestone"):
                title = service.hrd.getStr("milestone.title")
                description = service.hrd.getStr("milestone.description")
                deadline = service.hrd.getStr("milestone.deadline")
                owner = service.hrd.getStr("milestone.owner")
                name = service.instance
                
                repo.createMilestone(name, title, description, deadline, owner)

                milestonesSet.append(name)

    def get_issues_from_ays(self, service):
        repo = self.get_github_repo(service)
        issues = []
        Issue = j.clients.github.getIssueClass()
        for child in service.children:
            if child.role != 'github_issue':
                continue
            issue = Issue(repo=repo, ddict=child.model)
            issues.append(issue)

        return issues

    def get_github_repo(self,service):
        githubclientays=service.getProducers('github_client')[0]
        client = githubclientays.actions.getGithubClient(service=githubclientays)
        repokey = service.hrd.get("repo.account") + "/" + service.hrd.get("repo.name")
        return client.getRepo(repokey)

    @action()
    def set_labels(self, service):
        config = service.getProducers('github_config')[0]

        projtype = service.hrd.get("repo.type")
        labels = []

        for key, value in config.hrd.getDictFromPrefix("github.label").items():
            # label=key.split(".")[-1]
            label = key.replace(".", "_")
            if projtype in value or "*" in value:
                labels.append(label)

        r = self.get_github_repo(service)
        # first make sure issues get right labels
        r.labelsSet(labels, ignoreDelete=["p_"])

    @action()
    def processIssues(self, service, refresh=False):
        """
        refresh: bool, force loading of issue from github
        """
        self.set_labels(service=service)

        if service.state.get('processIssues', die=False) == 'RUNNING':
            # don't processIssue twice at the same time.
            j.logger.log('processIssue already running')
            return

        service.state.set('processIssues', 'RUNNING')
        service.state.save()

        repo = self.get_github_repo(service=service)
        if refresh:
            # force reload of services from github.
            repo._issues = None
        else:
            # load issues from ays.
            repo._issues = self.get_issues_from_ays(service=service)

        j.tools.github.process_issues(repo)

        for issue in repo.issues:
            args = {'github.repo': service.instance}
            service.aysrepo.new(name='github_issue', instance=str(issue.id), args=args, model=issue.ddict)

    def stories2pdf(self, service):
        repo = self.get_github_repo(service)
        raise NotImplementedError()

    @action()
    def recurring_process_issues_from_model(self, service):
        self.processIssues(service=service, refresh=False)

    @action()
    def recurring_process_issues_from_github(self, service):
        self.processIssues(service=service, refresh=True)

    def event_new_issue(self, service, event):
        event = j.data.models.cockpit_event.Generic.from_json(event)

        if event.args.get('source', None) != 'github' or \
                'key' not in event.args or \
                event.args.get('event', None) != 'issues':
            return

        data = j.core.db.hget('webhooks', event.args['key'])
        if data is None:
            return
        github_payload = j.data.serializer.json.loads(data.decode())
        action = github_payload.get('action', None)
        if action != 'opened':
            return

        # at this point we know we are interested in the event.
        repo = self.get_github_repo(service)
        # create issue object
        issue = repo.getIssue(github_payload['issue']['number'])
        # create service gitub_issue
        args = {'github.repo': service.instance}
        service.aysrepo.new(name='github_issue', instance=str(issue.id), args=args, model=issue.ddict)
