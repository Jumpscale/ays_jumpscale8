from JumpScale import j


class Actions(ActionsBaseMgmt):

#     def notify_telegram(self, ticket_url):
#         evt = j.data.models.cockpit_event.Telegram()
#         evt.io = 'output'
#         evt.args['chat_id'] =
#         msg = """*New support ticket received*
# Link to ticket: {url}
#         """.format(url=ticket_url)
#         evt.args['msg'] = msg
#         self.bot.sendMessage(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

    @action()
    def from_github_ticket(self, service, event):
        event = j.data.models.cockpit_event.Generic.from_json(event)

        if 'source' not in event.args or event.args['source'] != 'github':
            return

        if 'key' not in event.args:
            print("bad format of event")
            return
        key = event.args['key']
        data = j.core.db.hget('webhooks', event.args['key'])
        event_type = event.args['event']
        github_payload = j.data.serializer.json.loads(data)
        if event_type != 'issues':
            return
        action = github_payload['action']

        if action == 'opened':

            account = github_payload['repository']['owner']['login']
            name = github_payload['repository']['name']

            repo_service = None
            for s in service.producers['github_repo']:
                if name == s.hrd.getStr('repo.name') and account == s.hrd.getStr('repo.account'):
                    repo_service = s
                    break

            if repo_service is None:
                print("targeted repo is not monitored by this service.")
                # TODO, send email back to client to tell him
                return

            repo = repo_service.actions.get_github_repo(repo_service)
            issue = repo.getIssue(github_payload['issue']['number'])
            if issue.body.startswith('Ticket_'):
                # already processed
                # delete issue from redis
                j.core.db.hdel('webhooks', key)
                return

            # allocation of a unique ID to the Ticket
            guid = j.data.idgenerator.generateGUID()
            # Add ticket id in issue description
            issue.body = "Ticket_%s\n\n%s" % (guid, issue.body)
            # add labels to issue
            labels = issue.labels.copy()
            if 'type_assistance_request' not in labels:
                labels.append('type_assistance_request')
                issue.labels = labels
            # creation of the issue in the github repo
            repo.issues.append(issue)
            # Create issue service instance of the newly created github issue
            args = {'github.repo': repo_service.instance}
            service = service.aysrepo.new(name='github_issue', instance=str(issue.id), args=args, model=issue.ddict)

            # delete issue from redis when processed
            j.core.db.hdel('webhooks', key)


    @action()
    def from_email_ticket(self,service, event):
        email = j.data.models.cockpit_event.Email.from_json(event)

        if not email.subject.startswith('(Ticket)'):
            # this mail doesn't concerne us
            return

        # find for which repo is targeted by this email
        repo_name = ''
        for l in email.body.splitlines():
            if l.startswith("repository:"):
                repo_name = l[len("repository:"):].strip()
                break
            elif l.startswith("repo:"):
                repo_name = l[len("repo:"):].strip()
                break

        if repo_name == '':
            print("can't identify targeted repository")
            # TODO, send email back to client to tell him
            return

        repo_service = None
        for s in service.producers['github_repo']:
            if repo_name == s.hrd.getStr('repo.name'):
                repo_service = s
                break

        if repo_service is None:
            print("targeted repo is not monitored by this service.")
            # TODO, send email back to client to tell him
            return

        Issue = j.clients.github.getIssueClass()
        repo = repo_service.actions.get_github_repo(repo_service)
        # allocation of a unique ID to the Ticket
        guid = j.data.idgenerator.generateGUID()
        # Add ticket id in issue description
        body = "Ticket_%s\n\n" % guid
        body += email.body
        # creation of the issue in the github repo
        issue_obj = repo.api.create_issue(email.subject, body=body, labels=['type_assistance_request'])
        issue = Issue(repo=repo, githubObj=issue_obj)
        repo.issues.append(issue)
        # Create issue service instance of the newly created github issue
        args = {'github.repo': repo_service.instance}
        service = service.aysrepo.new(name='github_issue', instance=str(issue.id), args=args, model=issue.ddict)
