from JumpScale import j


class Actions(ActionsBaseMgmt):

    @action()
    def process(self, service):
        Issue = j.clients.github.getIssueClass()
        repo = service.parent.actions.get_github_repo(service=service.parent)

        from IPython import embed
        print ("DEBUG NOW process issue")
        embed()
        sdasd

        # only process this specific issue.
        for issue in repo.issues:
            if issue.id == service.model['id']:
                repo.process_issues([issue])
                break

    @action()
    def update_from_github(self, service, event):
        import datetime
        event = j.data.models.cockpit_event.Generic.from_json(event)

        if 'source' not in event.args or event.args['source'] != 'github':
            return

        if 'key' not in event.args:
            print("bad format of event")
            return

        data = j.core.db.hget('webhooks', event.args['key'])
        if data is None:
            return
        event_type = event.args['event']
        github_payload = j.data.serializer.json.loads(data.decode())

        action = github_payload.get('action', None)
        if action is None:
            return

        if github_payload['issue']['id'] != service.model['id']:
            # event not for this issue
            return

        if event_type == 'issue_comment':

            if action == 'created':
                model = service.model.copy()

                dt = datetime.datetime.strptime(github_payload['comment']['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
                comment = {
                    'body': github_payload['comment']['body'],
                    'id': github_payload['comment']['id'],
                    'time': j.data.time.any2HRDateTime(dt),
                    'url': github_payload['comment']['url'],
                    'user': github_payload['comment']['user']['login']
                }

                model['comments'].append(comment)
                service.model = model
                j.core.db.hdel('webhooks', event.args['key'])

            elif action == 'edited':
                model = service.model.copy()

                # find comment in model
                comment = None
                for i, comment in enumerate(model['comments']):
                    if comment['id'] == github_payload['comment']['id']:
                        break

                # update comment
                if comment is not None:
                    dt = datetime.datetime.strptime(github_payload['comment']['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
                    new_comment = {
                        'body': github_payload['comment']['body'],
                        'id': github_payload['comment']['id'],
                        'time': j.data.time.any2HRDateTime(dt),
                        'url': github_payload['comment']['url'],
                        'user': github_payload['comment']['user']['login']
                    }
                    # save new comment
                    model['comments'][i] = new_comment
                    service.model = model
                    j.core.db.hdel('webhooks', event.args['key'])
            elif action == 'deleted':
                model = service.model.copy()

                # find comment in model
                comment = None
                for i, comment in enumerate(model['comments']):
                    if comment['id'] == github_payload['comment']['id']:
                        model['comments'].remove(comment)

                service.model = model
                j.core.db.hdel('webhooks', event.args['key'])
            else:
                print('not supported action: %s' % action)
                return

        elif event_type == 'issues':

            if action == 'closed':
                model = service.model.copy()
                model['open'] = False
                model['state'] = 'closed'
                service.model = model

            elif action == 'reopened':
                model = service.model.copy()
                model['open'] = True
                model['state'] = 'reopened'
                service.model = model
            elif action in ['assigned', 'unassigned']:
                assignee = github_payload['issue']['assignee']
                if assignee is None:
                    service.model['assignee'] = ''
                else:
                    if j.data.types.list.check(assignee):
                        service.model['assignee'] = [a['login'] for a in assignee]
                    elif j.data.types.dict.check(assignee):
                        service.model['assignee'] = assignee['login']
            elif action in ['labeled', 'unlabeled']:
                service.model['labels'] = [i['name'] for i in github_payload['issue']['labels']]
            elif action == 'edited':
                service.model['body'] = github_payload['issue']['body']
            else:
                print('not supported action: %s' % action)
                return

        repo = service.parent.actions.get_github_repo(service=service.parent)
        issue = repo.getIssue(github_payload['issue']['number'])
        issue._ddict = service.model