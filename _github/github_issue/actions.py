from JumpScale import j


class Actions(ActionsBaseMgmt):

    @action()
    def process(self):
        Issue = j.clients.github.getIssueClass()
        repo = self.service.parent.actions.get_github_repo()

        # only process this specific issue.
        for issue in repo.issues:
            if issue.id == self.service.model['id']:
                repo.process_issues([issue])
                break

    @action()
    def getIssueFromGithub(self):

        repo=self.service.actions.get_github_repo()

        path=j.sal.fs.joinPaths(self.service.path,"issue.yaml")

        j.sal.fs.writeFile(path,str(md))

    @action()
    def update_from_github(self, event):
        import datetime
        event = j.data.models.cockpit_event.Generic.from_json(event)

        if 'source' not in event.args or event.args['source'] != 'github':
            return

        if 'key' not in event.args:
            print("bad format of event")
            return

        data = j.core.db.hget('webhooks', event.args['key'])
        event_type = event.args['event']
        github_payload = j.data.serializer.json.loads(data)

        action = github_payload['action']

        if event_type == 'issue_comment':

            if action == 'created':
                model = self.service.model.copy()

                dt = datetime.datetime.strptime(github_payload['comment']['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
                comment = {
                    'body': github_payload['comment']['body'],
                    'id': github_payload['comment']['id'],
                    'time': j.data.time.any2HRDateTime(dt),
                    'url': github_payload['comment']['url'],
                    'user': github_payload['comment']['user']['login']
                }

                model['comments'].append(comment)
                self.service.model = model
                j.core.db.hdel('webhooks', event.args['key'])

            elif action == 'edited':
                model = self.service.model.copy()

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
                    self.service.model = model
                    j.core.db.hdel('webhooks', event.args['key'])
            elif action == 'deleted':
                model = self.service.model.copy()

                # find comment in model
                comment = None
                for i, comment in enumerate(model['comments']):
                    if comment['id'] == github_payload['comment']['id']:
                        model['comments'].remove(comment)

                self.service.model = model
                j.core.db.hdel('webhooks', event.args['key'])
            else:
                print("not supported action")
        elif event_type == 'issues':
            import ipdb; ipdb.set_trace()
            if github_payload['issue']['id'] != self.service.model['id']:
                return

            if action == 'closed':
                model = self.service.model.copy()
                model['open'] = False
                model['state'] = 'closed'
                self.service.model = model

            elif action == 'reopened':
                model = self.service.model.copy()
                model['open'] = True
                model['state'] = 'reopened'
                self.service.model = model
