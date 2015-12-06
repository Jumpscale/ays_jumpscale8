from JumpScale import j
import json
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
    step5b: if check uptime was true will do stop action and retry the check_uptime_local configureheck
    step5c: if check uptime was true even after stop will do halt action and retry the check_uptime_local check
    step6: use the info in the hrd to start the application
    step7: do check_uptime_local to see if process starts
    step7b: do monitor_local to see if package healthy installed & running
    step7c: do monitor_remote to see if package healthy installed & running, but this time test is done from central location
    """

    def configure(self, serviceObj):
        data = {}
        data['PORT'] = serviceObj.hrd.getInt('port')
        data['POSTGRESQL'] = serviceObj.hrd.get('databasedsn')
        bindest = serviceObj.hrd.get('service.bindest')
        jsonfile = j.sal.fs.joinPaths(bindest, 'config.json')
        with open(jsonfile, 'w') as fl:
            json.dump(data, fl)
            
    def build(self, serviceObj):
        bashrc = os.environ['HOME'] + "/" + ".bashrc"
        if not os.path.exists('/opt/build/git.aydo.com/racktivity/rtpoller/src'):
            j.do.execute('mkdir /opt/build/git.aydo.com/racktivity/rtpoller/src')
        j.do.execute(". %s && GOPATH=$GOPATH:/opt/build/git.aydo.com/racktivity/rtpoller/ && cp -r /opt/build/git.aydo.com/racktivity/rtpoller/gorest/ /opt/build/git.aydo.com/racktivity/rtpoller/src && cd /opt/build/git.aydo.com/racktivity/rtpoller/src/gorest && godep restore && go build && cp /opt/build/git.aydo.com/racktivity/rtpoller/src/gorest/gorest /opt/code/git/binary/rtpoller/rtpoller/rtrelay" % bashrc)
        j.do.pushGitRepos(message="rtrelay new build", name='rtpoller', account='binary')