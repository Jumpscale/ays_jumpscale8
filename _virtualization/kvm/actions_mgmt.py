from JumpScale import j

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

    def prepareLocal(self, serviceObj):
        """
        This function is always exectued locally, even in the case of a remote install
        this gets executed before the files are downloaded & installed on approprate spots
        """
        def createBridgePub():
            node = None
            try:
                node = service.getproducer('node')
            except:
                # can't load producer
                return
            if node:
                conn = node._getSSHClient(node)
                cl = j.ssh.ubuntu.get(conn)
                script = """from JumpScale import j
    j.sal.nettools.setBasicNetConfigurationBridgePub()
    """
            cl.executeRemoteTmuxJumpscript(script)
        j.actions.start(retry=2, name="createBridgePub",description='create public brigde on remote node', cmds=createBridgePub, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj) 

    def prepare(self,serviceObj):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """

        ##now part of jp.hrd
        # def deps():
        #     cmd="apt-get update"
        #     rc,out,err=j.do.execute( cmd, outputStdout=True, outputStderr=True, useShell=True, log=True, cwd=None, timeout=360, captureout=True, dieOnNonZeroExitCode=False)

        #     if not j.do.exists("/usr/bin/virsh"):
        #         cmd="apt-get install qemu-kvm qemu python-libvirt virt-viewer libvirt-bin bridge-utils lrzip -y"
        #         rc,out,err=j.do.execute( cmd, outputStdout=True, outputStderr=True, useShell=True, log=True, cwd=None, timeout=360, captureout=True, dieOnNonZeroExitCode=False)

        # j.actions.start(retry=2, name="deps",description='install deps', cmds='', action=deps, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj) 


        C="""
apt-get install curlftpfs -y
mkdir -p /mnt/ftp
curlftpfs pub:pub1234@ftp.aydo.com /mnt/ftp
mkdir -p /mnt/vmstor/kvm/images
#rsync -arv --partial --progress /mnt/ftp/images/ubuntu1404/ /mnt/vmstor/kvm/images/ubuntu1404/
#rsync -arv --partial --progress /mnt/ftp/images/ubuntu1410/ /mnt/vmstor/kvm/images/ubuntu1410/
rsync -arv --partial --progress /mnt/ftp/images/openwrt/ /mnt/vmstor/kvm/images/openwrt/
"""

        j.actions.start(retry=2, name="getimages",description='get ubuntu & openwrt images (can take a while)', cmds=C, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj) 

        def unpack():
            for item in j.sal.fs.listFilesInDir( "/mnt/vmstor/kvm/images/", recursive=True, filter="*.lrz", followSymlinks=True, listSymlinks=False):
                cmd="lrzip -d %s"%item
                j.do.executeInteractive(cmd)
                j.do.delete(item)
                
        unpack()


    def configure(self, serviceObj):

        def setnetwork():
            import JumpScale.lib.kvm
            j.sal.kvm.initPhysicalBridges()
            # j.sal.kvm.initLibvirtNetwork()

        j.actions.start(retry=2, name="setnetwork",description='setnetwork', cmds='', action=setnetwork, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj) 

    def removedata(self, serviceObj):
        pass

    def build(self, serviceObj):
        def prepare_build():
            j.sal.ubuntu.checkInstall(["cmake"], "cmake")

            cmd='apt-get update && apt-get install --no-install-recommends -y libglib2.0-dev libpixman-1-dev autoconf libtool build-essential'
            j.do.executeInteractive(cmd)


        j.actions.start(retry=2, name="prepare_build",description='', cmds='', action=prepare_build, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)
        
        cmd = """
set -e
cd /opt/build/git.aydo.com/aydo/qemu-ledis
./configure --target-list="x86_64-softmmu x86_64-linux-user" --enable-debug --prefix=/opt/jumpscale8/apps/kvm
make
make DESTDIR="/opt/code/git/binary/kvm/root" install
mv /opt/code/git/binary/kvm/root/opt/jumpscale8/apps /opt/code/git/binary/kvm/root/
rm -rf /opt/code/git/binary/kvm/root/opt
"""
        j.actions.start(retry=1, name="qemu-ledis",description='compile qemu ledis', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)


    def cleanup(self, serviceObj):
        pass