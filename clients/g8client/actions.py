from JumpScale import j


def input(job):
    args = job.model.args
    if "account" not in args or args["account"].strip() == "":
        args['account'] = args["login"]

    return args
