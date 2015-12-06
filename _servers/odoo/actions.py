from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

import os.path

def log(message):
    print((' :: ' + message))

class Actions(ActionsBase):

    def build(self,serviceObj):
        
        BUILD_BASE = '/opt/build/odoo'
        PKG = BUILD_BASE + '/pkg'
        j.sal.fs.createDir(BUILD_BASE)

        APT_DEPS = ('libpq-dev', 'libxml2-dev', 'libxslt1-dev', 'python-dev', 'libldap2-dev', 'libsasl2-dev', 'python-virtualenv') 
        for dep in APT_DEPS:
            log('Installing ubuntu dep: ' + dep)
            j.sal.ubuntu.install(dep)
        
        SOURCE_TARBALL_URL = 'https://github.com/odoo/odoo/archive/8.0.0.tar.gz'
        log('Downloading source tarball')
        local_file = os.path.join(BUILD_BASE, 'odoo.tar.gz')
        j.sal.nettools.downloadIfNonExistent(SOURCE_TARBALL_URL, local_file, md5_checksum='a92253ea9e07b9bca7f1a4de2bb7d371')

        log('Extracting downloaded files')
        uncompressed_path = os.path.join(BUILD_BASE, 'uncompressed')
        j.sal.fs.targzUncompress(local_file, uncompressed_path)

        if j.sal.fs.exists(PKG):
            j.sal.fs.removeDirTree(PKG)

        log('Copying over the extracted files')
        j.sal.fs.copyDirTree(os.path.join(uncompressed_path, 'odoo-8.0.0'), PKG)
        
        def python_deps():
            return open(os.path.join(PKG, 'requirements.txt')).read().split()

        for python_dep in python_deps():
            install_path = os.path.join(PKG, 'pip-' + python_dep)
            install_command = 'pip install --exists-action=w --target="%(target)s" %(dep)s' % {'dep': python_dep, 'target': install_path}
            log(install_command)
            j.actions.start(name='pip install ' + python_dep, cmds=install_command, serviceObj=serviceObj)
            copy_command = 'cp -r %(install_path)s/* %(pkg_path)s/' % {'install_path': install_path, 'pkg_path': PKG}
            log(copy_command)
            j.actions.start(name='pip copy installed ' + python_dep, cmds=copy_command, serviceObj=serviceObj)

            # Delete all the leftover 'pip-*' directories
            command = 'rm -r %s/pip-*' % PKG
            log(command)
            j.actions.start(name='pip delete leftover pip files', cmds=command, serviceObj=serviceObj)
            
            # Install npm dependencies
            for npm_dep in ('less', 'less-plugin-clean-css'):
                command = '/opt/nodejs/bin/npm install -g ' + npm_dep
                j.actions.start(name='npm-install ' + npm_dep, cmds=command, serviceObj=serviceObj)
            

    def configure(self, serviceObj):

        if not j.system.unix.unixUserExists('odoo'):
            j.system.unix.addSystemUser('odoo', homedir='/var/lib/odoo')
            j.tools.cuisine.local.user_ensure(name, passwd=None, home=None, uid=None, gid=None, shell=None, fullname=None, encrypted_passwd=True)
            
        user_commands = 'sudo -u postgres /opt/postgresql/bin/createuser -s -w $(param.db.user); sudo -u postgres /opt/postgresql/bin/psql --command "ALTER USER $(param.db.user) WITH PASSWORD \'$(param.db.password)\'"' 
        j.actions.start(name='Create Postgresql odoo user', cmds=user_commands, serviceObj=serviceObj)

        # Copy over the files from the model_database
        j.sal.fs.copyDirTree(os.path.join(serviceObj.hrd.get('param.base'), 'model_database/filestore'), '/var/lib/odoo/.local/share/Odoo/filestore')
        j.sal.fs.chown('/var/lib/odoo/', 'odoo')
        
        # Load the database dump from model_databasse
        commands = 'sudo -u $(param.db.user) /opt/postgresql/bin/createdb codescalers ; sudo -u $(param.db.user) /opt/postgresql/bin/psql -f %(sql_dump_path)s codescalers' % {'sql_dump_path': os.path.join(serviceObj.hrd.get('param.base'), 'model_database/dump.sql')}
        j.actions.start(name='Load model database image', cmds=commands, serviceObj=serviceObj)
