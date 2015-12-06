from JumpScale import j
from io import StringIO
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

        domain = serviceObj.hrd.get('param.ad.domain')
        realm  = serviceObj.hrd.get('param.ad.realm')
        passwd = serviceObj.hrd.get('param.ad.adminpwd')
        myaddr = serviceObj.hrd.get('param.ad.ipaddr')
        remote = serviceObj.hrd.get('param.ad.remote')
        host   = j.system.net.getHostname()

        print('Joining Active Directory', realm, '/', myaddr)

        # Update resolv.conf
        j.sal.fs.writeFile('/etc/resolv.conf', "domain " + realm + "\n", False)
        j.sal.fs.writeFile('/etc/resolv.conf', "nameserver " + remote + "\n", True)

        # Setup /etc/hosts
        # eg: 172.17.0.1      18dadc4c034c.dc1.domain.tld 18dadc4c034c
        hosts = StringIO('\n'.join(line.strip() for line in open('/etc/hosts'))).getvalue()
        if not realm in hosts:
            j.sal.fs.writeFile('/etc/hosts', "\n" + myaddr + "\t" +  host + "." + realm + " " + host + "\n", True)

        # Building config files
        j.sal.fs.copyFile(base + '/smb.member.conf', '/etc/samba/smb.conf')
        
        if j.sal.fs.exists('/etc/krb5.keytab'):
            j.sal.fs.unlinkFile('/etc/krb5.keytab')

        data = {
            'hostname': host,
            'workgroup': domain.upper(),
            'realm': realm
        }

        hrd = j.core.hrd.getHRDFromDict(data)
        hrd.applyOnFile('/etc/samba/smb.conf')

        # Joining domain
        j.sal.process.run("net ads join -U Administrator%" + passwd, True, False, 10, False)
        
        # Starting daemons
        serviceObj.start()

        # Enable remote auth with nsswitch.conf
        # passwd: compat winbind
        # group:  compat winbind
        nss = StringIO('\n'.join(line.strip() for line in open('/etc/nsswitch.conf'))).getvalue()
        if not "winbind" in nss:
            print('Setting winbind in nsswitch')
            nss = nss.replace("passwd:         compat", "passwd:         compat winbind")
            nss = nss.replace("group:          compat", "group:          compat winbind")
            j.sal.fs.writeFile('/etc/nsswitch.conf', nss + "\n")

        # Checking if it works (FIXME: net ads testjoin ?)
        output = j.sal.process.run("wbinfo -u", False, True, 10, False)
        if "krbtgt" in output[1]:
            print('Active Directory response seems correct, have a nice day !')
            return True
            
        else:
            print('Integration seems not working, please check !')
            return False
