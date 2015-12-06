from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassTmpl()


class Actions(ActionsBase):

    def build(self, serviceObj, output_path="/mnt/dedupe"):
        folders = serviceObj.installRecipe()

        for src, dest in folders:
            j.tools.sandboxer.dedupe(dest, output_path, '%s__%s' % (serviceObj.domain, serviceObj.name))

    def init(self, serviceObj, args):
        super(Actions, self).init(serviceObj, args)
        if 'tcp.addr' not in args or args['tcp.addr'] == '':
            args['tcp.addr'] = 'localhost'
