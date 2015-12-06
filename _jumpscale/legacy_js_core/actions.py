from JumpScale import j

import os
import imp

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def build(self, service_obj):
        root = '/opt/build/github.com/Jumpscale/jumpscale_core8'
        binary = '/opt/code/git/binary/legacy_js_core/domains'

        j.sal.fs.removeDirTree(binary)

        def pack(_, path):
            module = imp.load_source(path, path)
            domain = module.organization
            basename = os.path.splitext(j.sal.fs.getBaseName(path))[0]

            name = getattr(module, 'name', basename)
            dst_folder = j.sal.fs.joinPaths(binary, domain)
            j.sal.fs.createDir(dst_folder)

            j.sal.fs.copyFile(path, j.sal.fs.joinPaths(dst_folder, '%s.py' % name))

        j.system.fswalker.walk(
            j.sal.fs.joinPaths(root, 'apps', 'agentcontroller', 'jumpscripts'),
            pack,
            pathRegexIncludes=['.*\.py$'])

        j.do.pushGitRepos(
            message='legacy_js_core  new build',
            name='legacy_js_core',
            account='binary'
        )
