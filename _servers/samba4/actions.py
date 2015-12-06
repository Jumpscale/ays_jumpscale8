from JumpScale import j
import signal

ActionsBase=j.atyourservice.getActionsBaseClass()

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
    def prepare(self,serviceObj):
        """
        this gets executed before the files are downloaded & installed on appropriate spots
        """
        return True

    def configure(self,serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the ays if anything needs to be started
        """
        base = j.application.config.get('system.paths.base')
        base = base + '/apps/samba4'
        
        # Install sernet repository on system
        j.sal.process.run("dpkg -i " + base + "/sernet-samba-keyring_1.4_all.deb", True, False)

        # Check if sources.list contains sernet packages server
        if 'download.sernet.de/packages/samba/4.2/ubuntu' not in open('/etc/apt/sources.list').read():
            print('Adding sources.list sernet repository')
            j.sal.fs.writeFile('/etc/apt/sources.list', "\n", True)
            j.sal.fs.writeFile('/etc/apt/sources.list', "# Samba sernet\n", True)
            j.sal.fs.writeFile('/etc/apt/sources.list', "deb https://sernet-samba-public:Noo1oxe4zo@download.sernet.de/packages/samba/4.2/ubuntu trusty main\n", True)

            # Update packages list
            j.sal.ubuntu.updatePackageMetadata()

        # Install samba
        j.sal.ubuntu.install("sernet-samba-client sernet-samba-ad")
        j.sal.fs.createDir('/var/run/samba/')
        
        # Saving old files
        if j.sal.fs.exists('/etc/samba/smb.conf'):
            j.sal.fs.copyFile('/etc/samba/smb.conf', '/etc/samba/smb.conf.bak')

        return True
