from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassTmpl()


class Actions(ActionsBase):

    def build(self, serviceObj, output_path="/mnt/dedupe"):
        folders = serviceObj.installRecipe()

        for src, dest in folders:
            j.tools.sandboxer.dedupe(dest, output_path, '%s__%s' % (serviceObj.domain, serviceObj.name))
