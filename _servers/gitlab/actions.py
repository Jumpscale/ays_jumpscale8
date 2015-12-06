from JumpScale import j
import time
import os

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def prepare(self, serviceObj):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """
        def createUser():
            j.do.execute('sudo locale-gen && sudo dpkg-reconfigure locales && export LC_ALL=$LANG && export LANGUAGE=$LANG')

            # Add git user
            j.system.unix.addSystemUser('git', groupname='root', shell='/bin/bash', homedir='/home/git')
j.tools.cuisine.local.user_ensure(name, passwd=None, home=None, uid=None, gid=None, shell=None, fullname=None, encrypted_passwd=True)
            j.do.createDir('/home/git/gitlab')
            j.do.createDir('/home/git/gitlab-shell')

            # is this required ??
            j.do.copyFile('/etc/login.defs', '/etc/login.defs.org')
            j.do.execute("cd /etc/ && sed 's/ENV_PATH\tPATH=.*/ENV_PATH\tPATH=\/opt\/jumpscale8\/bin:\/opt\/postgresql\/bin:\/opt\/jumpscale8\/apps\/redis:\/usr\/local\/sbin:\/usr\/local\/bin:\/usr\/sbin:\/usr\/bin:\/sbin:\/bin:\/usr\/games:\/usr\/local\/games:\/opt\/ruby\/bin/' login.defs.org | tee login.defs")
            j.do.execute('chmod +w /etc/sudoers')
            j.do.copyFile('/etc/sudoers', '/etc/sudoers.org')
            j.do.execute("cd /etc/ && sed 's/Defaults\tsecure_path=.*/Defaults\tsecure_path=\/opt\/jumpscale8\/bin:\/opt\/postgresql\/bin:\/opt\/jumpscale8\/apps\/redis:\/usr\/local\/sbin:\/usr\/local\/bin:\/usr\/sbin:\/usr\/bin:\/sbin:\/bin:\/usr\/games:\/usr\/local\/games:\/opt\/ruby\/bin/' /etc/sudoers.org | tee /etc/sudoers")

        j.actions.start(description='create git user', name='gitUser', action=createUser, serviceObj=serviceObj)

        return True

    def configure(self, serviceObj):

        def postgresqlSetup():
            # Postgresql partation
            try:
                j.do.execute('cd /opt/postgresql/bin; sudo -u postgres /opt/postgresql/bin/psql -d template1 -c \'CREATE USER git CREATEDB\'')
                j.do.execute('cd /opt/postgresql/bin; sudo -u postgres /opt/postgresql/bin/psql -d template1 -c \'CREATE DATABASE gitlabhq_production OWNER git\'')
            except Exception as e:
                print(e.message)
        j.actions.start(description='create database in postgresql', name='postgresql', action=postgresqlSetup, serviceObj=serviceObj)

        def gitlabSetup():
            # Install gitlab
            j.sal.fs.createDir('/home/git/repositories')
            j.sal.fs.createDir('/home/git/gitlab-satellites')
            j.sal.fs.chown('/home/git/', 'git')
            j.sal.fs.chmod('/home/git/gitlab-satellites', 0o2770)

            j.do.copyFile('/home/git/gitlab/lib/support/init.d/gitlab.default.example', '/etc/default/gitlab')
            j.do.copyFile('/home/git/gitlab/lib/support/logrotate/gitlab', '/etc/logrotate.d/gitlab')
            j.sal.fs.chown('/home/git', 'git')

            j.sal.fs.chmod('/opt/jumpscale8/var/redis/gitlab/redis.sock', 0o755)
            j.sal.fs.chown('/opt/jumpscale8/var/redis/gitlab/redis.sock', 'git')
        j.actions.start(description='config environment for gitlab', name='gitlabEnv', action=gitlabSetup, serviceObj=serviceObj)

        def nginxSetup():
            # Configure Enginx
            if not j.do.isFile('/opt/nginx/cfg/sites-available/gitlab'):
                j.do.copyFile('/home/git/gitlab/lib/support/nginx/gitlab', '/opt/nginx/cfg/sites-available/gitlab')
            if not j.do.isFile('/opt/nginx/cfg/sites-enabled'):
                j.do.createDir('/opt/nginx/cfg/sites-enabled')
            if not j.do.isLink('/opt/nginx/cfg/sites-enabled/gitlab'):
                j.do.execute('ln -s /opt/nginx/cfg/sites-available/gitlab /opt/nginx/cfg/sites-enabled/gitlab')
                j.do.delete('/opt/nginx/cfg/sites-enabled/default')
        j.actions.start(description='config nginx', name='nginx', action=nginxSetup, serviceObj=serviceObj)

        def rakeSetup():
            os.system("cd /home/git/gitlab && sudo -u git -H bundle exec rake gitlab:setup RAILS_ENV=production")
        j.actions.start(description='rake setup', name='rake', action=rakeSetup, serviceObj=serviceObj)

        nginx = j.atyourservice.get(name='nginx')
        nginx.restart()
        print('userName: root\npassword: 5iveL!fe')
        return True
