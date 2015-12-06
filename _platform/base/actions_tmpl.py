from JumpScale import j

ActionsBaseTmpl=j.atyourservice.getActionsBaseClassTmpl()

class Actions(ActionsBaseTmpl):

    def build(self,serviceObj):
        """
        """

        # paths=[]
        # paths.append("/usr/lib/python2.7/")
        # paths.append("/usr/local/lib/python2.7/")

        # excludeFileRegex=["/xml/","-tk/","/xml","/lib2to3"]
        # excludeDirRegex=["/JumpScale","\.dist-info","config-x86_64-linux-gnu"]

        # dest = "/opt/jumpscale8/lib"

        # for path in paths:
        #     j.tools.sandboxer.copyTo(path,dest,excludeFileRegex=excludeFileRegex,excludeDirRegex=excludeDirRegex)

        # try:
        #     j.do.copyFile("/usr/bin/python","/opt/jumpscale8/bin/python")
        # except Exception,e:
        #     print e
            
        # j.tools.sandboxer.copyLibsTo(dest,"/opt/jumpscale8/bin/",recursive=True)

        serviceObj.upload2AYSfs("/opt/jumpscale8")


