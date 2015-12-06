from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassTmpl()


class Actions(ActionsBase):

    def build(self, serviceObj, output_path="/mnt/dedupe"):
        key = '%s__%s' % (serviceObj.domain, serviceObj.name)

        folders = serviceObj.installRecipe()
        for src, dest in folders:
            j.tools.sandboxer.dedupe(dest, output_path, key, append=False, reset=True)

        cmd = 'apt-get clean; apt-get install -yd libgd3'
        j.do.execute(cmd)
        for f in j.sal.fs.listFilesInDir('/var/cache/apt/archives', filter='*.deb'):
            print("extract %s" % f)
            cmd = 'dpkg --extract %s .' % f
            j.do.execute(cmd)

        for f in j.sal.fs.listFilesInDir('lib', recursive=True):
            j.sal.fs.copyFile(f, '/opt/jumpscale8/bin/')
            dest = j.sal.fs.joinPaths('/opt/jumpscale8/bin/', j.sal.fs.getBaseName(f))
            print("add %s to metadata" % dest)
            j.tools.sandboxer.dedupe(dest, output_path, key, append=True)

        for f in j.sal.fs.listFilesInDir('usr/lib', recursive=True):
            if not j.sal.fs.exists(f):
                continue
            j.sal.fs.copyFile(f, '/opt/jumpscale8/bin/')
            dest = j.sal.fs.joinPaths('/opt/jumpscale8/bin/', j.sal.fs.getBaseName(f))
            print("add %s to metadata" % dest)
            j.tools.sandboxer.dedupe(dest, output_path, key, append=True)
