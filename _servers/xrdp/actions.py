from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    def install(self,serviceObj):

        cmd="""
        # remove some possible stale cruft
        rm -f /var/run/xrdp/xrdp*.pid

        # Start xrdp server
        set -ex
        service xrdp start

        # get a wm & env
        apt-get install xubuntu-desktop gksu
        
        # this xubuntu-desktop should be themed more properly

        # add some user & passwd
        useradd -c "Demo User" -m -s /bin/bash demo
        passwd demo
        # add session type for xrdp login
        echo xfce4-session > /home/demo/.xsession
        """
        j.actions.start(retry=1, name="xrdp",description='', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)
        print("install")
        from IPython import embed;embed()

    def build(self,serviceObj):
        cmd="""
        unset LD_LIBRARY_PATH
        apt-get update
        apt-get install build-essential -y
        apt-get install dialog -y
        apt-get install bash-completion -y
        apt-get install python-dev -y

        # Create and start xrdp
        set -ex
        cd /opt/build/github.com/scarygliders/X11RDP-o-Matic/
        bash X11rdp-o-matic.sh --justdoit # will take at least half an hour on a beefed machine

        # in ~/X11RDP-o-Matic/packages/*/*.deb

        """
        # print cmd
        print("build")
        j.do.executeBashScript(cmd)
        

        from IPython import embed;embed()

        j.do.createDir("/opt/code/git/binary/xrdp/pkg")
        j.do.copyTree("/opt/build/github.com/scarygliders/X11RDP-o-Matic/packages/x11rdp/", dest="/opt/code/git/binary/xrdp/pkg/", deletefirst=True)
        j.do.copyTree("/opt/build/github.com/scarygliders/X11RDP-o-Matic/packages/xrdp/", dest="/opt/code/git/binary/xrdp/pkg/", deletefirst=True)

        

        # source="/opt/go/myproj/bin/weed"
        # j.do.createDir("/opt/weedfs")
        # j.do.copyFile(source,"/opt/weedfs/weed")


