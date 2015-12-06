from JumpScale import j
from io import StringIO
import os

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
    def configure(self,serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the ays if anything needs to be started
        """
        """
        sudo apt-get install build-essential git libfuse-dev libcurl4-openssl-dev libxml2-dev mime-support automake libtool
        sudo apt-get install pkg-config libssl-dev # See (*3)
        git clone https://github.com/s3fs-fuse/s3fs-fuse
        cd s3fs-fuse/
        ./autogen.sh
        ./configure --prefix=/usr --with-openssl # See (*1)
        make
        sudo make install
        """
        
        j.sal.ubuntu.install("build-essential git libfuse-dev libcurl4-openssl-dev libxml2-dev mime-support automake libtool")
        j.sal.ubuntu.install("pkg-config libssl-dev")
        
        
        # FIXME: git clone another way ?
        j.sal.process.run("git clone https://github.com/s3fs-fuse/s3fs-fuse", True, False)
        os.chdir("s3fs-fuse")
        j.sal.process.run("./autogen.sh", True, False)
        
        # FIXME: /opt as variable
        j.sal.process.run("./configure --prefix=/opt/s3fs-fuse --with-openssl", True, False)
        
        j.sal.process.run("make", True, False)
        j.sal.process.run("make install", True, False)
