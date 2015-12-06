from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        nfs = j.ssh.nfs.get(j.ssh.connect())

        def askInfo(i):
            info = None
            name = 'hrd.shares.%d' % i
            if serviceObj.hrd.exists(name):
                info = serviceObj.hrd.get(name, None)
            if not info:
                info = {}
                info['path'] = j.tools.console.askString("Path of the folder to expose", '/mnt/storage/')
                info['host'] = j.tools.console.askString("Host allow to mount the folder")
                info['options'] = j.tools.console.askString("options", 'root_no_squash, no_subtree_check')
            return info

        nbr = serviceObj.hrd.getInt('nfs.nbrshares')
        paths = [cl.path for cl in nfs.exports]
        for x in range(0, nbr):
            info = askInfo(x)
            if info['path'] in paths:
                nfs.delete(info['path'])
            else:
                share = nfs.add(info['path'])
                share.addClient(info['host'], info['options'])
            serviceObj.hrd.set('shares.%d' % x, info)
        nfs.commit()
