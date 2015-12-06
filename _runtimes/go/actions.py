from JumpScale import j
from urllib2 import urlparse
import os

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):
    """
    process for install
    -------------------
    step1: prepare actions
    step2: check_requirements action
    step3: download files & copy on right location (hrd info is used)
    step4: configure action
    step5: check_uptime_local to see if process stops  (uses timeout $process.stop.timeout)
    step5b: if check uptime was true will do stop action and retry the check_uptime_local check
    step5c: if check uptime was true even after stop will do halt action and retry the check_uptime_local check
    step6: use the info in the hrd to start the application
    step7: do check_uptime_local to see if process starts
    step7b: do monitor_local to see if package healthy installed & running
    step7c: do monitor_remote to see if package healthy installed & running, but this time test is done from central location
    """

    def prepare(self, serviceObj):
        j.sal.ubuntu.install("gcc")

    def configure(self, serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the ays if anything needs to be started
        """

        serviceObj.hrd.set('goroot', serviceObj.hrd.getStr('service.base', '/opt/go'))

        def createGOPATH():
            # create GOPATH
            if not j.sal.fs.exists('$(gopath)'):
                j.sal.fs.createDir('$(gopath)')
                j.sal.fs.createDir(j.sal.fs.joinPaths('$(gopath)', "pkg"))
                j.sal.fs.createDir(j.sal.fs.joinPaths('$(gopath)', "src"))
                j.sal.fs.createDir(j.sal.fs.joinPaths('$(gopath)', "bin"))

        j.actions.start(name="create GOPATH", description='create GOPATH', action=createGOPATH,  die=True, stdOutput=True, serviceObj=serviceObj)

    def buildProject(self, serviceObj, package=None, generate=False):
        """
        you can call this method from another service action.py file to build a go project
        """
        if package is None:
            j.events.inputerror_critical(msg="package can't be none", category="go build", msgpub='')

        gopath = serviceObj.hrd.get('gopath')
        goroot = serviceObj.hrd.get('goroot')
        gobin = j.sal.fs.joinPaths(goroot, 'bin/go')
        env = os.environ
        env.update({
            'GOPATH': gopath,
            'GOROOT': goroot
        })
        getcmd = '%s get -a -u -v %s' % (gobin, package)
        generatecmd = '%s get generate %s' % (gobin, package)
        re, out, err = 0, '', ''
        try:
            if generate:
                print("start : %s" % generate)
                re, out, err = j.sal.process.run(getcmd, env=env, maxSeconds=60,  showOutput=True, captureOutput=False)
                print("go generate succeed" if re == 0 else "error during go generate")

            print("start : %s" % getcmd)
            re, out, err = j.sal.process.run(getcmd, env=env, maxSeconds=60,  showOutput=True, captureOutput=False)
            print("go get succeed" if re == 0 else "error during go get")
        except Exception as e:
            print(e.msg)

    def buildProjectGodep(self, serviceObj, package=None, generate=False):
        """
        you can call this method from another service action.py file to build a go project
        :param package: URL to package to build (https://github.com/...)
        """
        if package is None:
            j.events.inputerror_critical(msg="package can't be none", category="go build", msgpub='')

        url = urlparse.urlparse(package)

        gopath = serviceObj.hrd.get('gopath')
        goroot = serviceObj.hrd.get('goroot')
        gobin = j.sal.fs.joinPaths(goroot, 'bin/go')
        godepbin = j.sal.fs.joinPaths(gopath, 'bin/godep')

        dest = '%s/src/%s' % (gopath, url.hostname + url.path)
        j.sal.fs.removeDirTree(dest)

        env = os.environ
        newenv = {
            'GOPATH': gopath,
            'GOROOT': goroot,
            'PATH': '%s/bin:%s' % (goroot, env['PATH'])
        }

        cmds = [
            '%s get github.com/tools/godep' % gobin,
            'git clone %s %s' % (package, dest),
            'cd %s && %s restore' % (dest, godepbin),
        ]
        if generate:
            cmds.append('cd %s && %s go generate' % (dest, godepbin))
        cmds.append('cd %s && %s go install' % (dest, godepbin))

        for cmd in cmds:
            print("%s: start" % cmd)
            re, out, err = j.sal.process.run(cmd, env=newenv, showOutput=True, captureOutput=False,
                                                stopOnError=False)
            if re != 0:
                raise RuntimeError('Failed to execute %s - (%s, %s, %s)' % (cmd, re, out, err))

            print("%s: succeed" % cmd if re == 0 else "%s: error" % cmd)

    def removedata(self, serviceObj):
        j.sal.fs.removeDirTree("/opt/go")
