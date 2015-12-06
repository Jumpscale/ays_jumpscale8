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
    
    """
    === Uninstall ===
    killall samba
    apt-get remove -y --purge samba* sernet*
    apt-get autoremove -y --purge
    rm -rfv /opt/jumpscale8/hrd/apps/jumpscale__samba4*
    rm -rfv /var/cache/samba/ /var/lib/samba/ /tmp/samba4/ /run/samba/ /var/log/samba/ /etc/samba/
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
        
        domain = serviceObj.hrd.get('param.ad.domain')
        realm  = serviceObj.hrd.get('param.ad.realm')
        passwd = serviceObj.hrd.get('param.ad.adminpwd')
        
        print('Setting up new Active Directory:', realm, '/', domain)

        # Provision AD
        options = "--domain " + domain + " --realm " + realm + " --adminpass " + passwd
        j.sal.process.run("samba-tool domain provision --use-rfc2307 " + options, True, False)
        
        # Building uid/gid
        print('Building initial unix uid/gid for domain users')
        j.sal.fs.copyFile(base + '/update-uid.sh', '/etc/samba/update-uid.sh')
        j.sal.process.run("bash " + base + "/update-uid.sh", True, False)

        # Update resolv.conf
        j.sal.fs.writeFile('/etc/resolv.conf', "domain " + realm + "\n", False)
        j.sal.fs.writeFile('/etc/resolv.conf', "nameserver 127.0.0.1\n", True)

        return True
