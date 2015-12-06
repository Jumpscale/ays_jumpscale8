import os

from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):
    def build(self, service_obj):
        bashrc = os.environ['HOME'] + "/" + ".bashrc"

        root = '/opt/build/git.aydo.com/0-complexity/hubble'

        src = '{root}/src'.format(root=root)

        if not os.path.exists(src):
            j.do.execute(
                'mkdir %s' % src
            )

        cmd = (
            '. {bashrc} && GOPATH=$GOPATH:{root}/ && cp -r {root}/hubble/ ' +
            '{root}/src && cd {root}/src/hubble/ && godep get && cd ./main' +
            ' && go build proxy.go && go build agent.go && ' +
            'cp {root}/src/hubble/main/proxy {root}/src/hubble/main/agent ' +
            '/opt/code/git/binary/hubble'
        ).format(bashrc=bashrc, root=root)

        j.do.execute(cmd)
        j.do.pushGitRepos(
            message='hubble new build',
            name='hubble',
            account='binary'
        )
