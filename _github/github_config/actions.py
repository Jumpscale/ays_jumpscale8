from JumpScale import j



class Actions():

    def init(self):

        config="""
        github.label.priority.critical: ['*']
        github.label.priority.minor: ['*']
        github.label.priority.normal: ['*']
        github.label.priority.urgent: ['*']
        github.label.process.duplicate: ['*']
        github.label.process.wontfix: ['*']
        github.label.state.inprogress: ['*']
        github.label.state.question: ['*']
        github.label.state.verification: ['*']
        github.label.type.bug: [code, ays, cockpit, doc, www]
        github.label.type.feature: [code, ays, cockpit, doc, www]
        github.label.type.monitor: [proj, www, cockpit]
        github.label.type.question: [home, code, proj, ays, doc, cockpit, www,milestone]
        github.label.type.story: [home, proj, milestone]
        github.label.type.task: [home,milestone,proj]
        github.label.type.ticket: [proj]
        github.label.type.lead: [proj]
        github.project.types: [home, proj, cockpit, doc, ays, code, www, milestone]
        """

        j.data.text.strip(config)

        labels=j.data.serializer.yaml.loads(config)

        self.service.hrd.setArgs(labels)

    def getGithubClient(self):
        from github import Github
        g=Github("$(github.secret)")
        return g

    def install(self):
        self.monitor()

    def monitor(self):
        g=self.getGithubClient()


        