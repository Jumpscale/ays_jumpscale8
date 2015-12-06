from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClassNode()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        if serviceObj.hrd.getBool("docker.build"):
            dest = j.do.pullGitRepo("$(docker.build.repo)")
            cmd = "cd %s; sh build_docker.sh" % dest
            print("start image building, it can't take a long time.")
            rc, out = j.sal.process.execute(cmd, dieOnNonZeroExitCode=True, outputToStdout=True)
            if rc != 0:
                j.j.events.opserror_critical(msg="error while building docker image %s : %s" \
                                             % ("$(docker.image)", out), category="docker_build")

            if serviceObj.hrd.getBool("docker.upload"):
                cmd = "docker push $(docker.image)"
                print("start pushing of image to docker hub, it can't take a long time.")
                rc, out = j.sal.process.execute(cmd, dieOnNonZeroExitCode=True, outputToStdout=True)
                if rc != 0:
                    j.j.events.opserror_critical(msg="error while pushing docker image %s to docker hub : %s" \
                                                 % ("$(docker.image)", out), category="docker_build")

        keys = j.do.listSSHKeyFromAgent()
        if len(keys) <= 0:
            j.events.opserror_critical(msg="can't find any ssh key available", category="docker_build")
        port = j.sal.docker.create(name="build_%s" % serviceObj.instance, stdout=True, base="$(docker.image)",
                                     ports="", vols="", sshpubkey=keys[0], jumpscale=False, sharecode=False)
        serviceObj.hrd.set("ssh.port", port)

        cl = j.remote.cuisine.connect('localhost', port)
        cl.file_write('/root/.ssh/config', """Host *
    StrictHostKeyChecking no""")

        return 'nr'

    def start(self, serviceObj):
        j.sal.docker.restart("build_%s" % serviceObj.instance)

    def stop(self, serviceObj):
        j.sal.docker.stop("build_%s" % serviceObj.instance)

    def removedata(self, serviceObj):
        """
        delete docker container
        """
        j.sal.docker.destroy("build_%s" % serviceObj.instance)
        return True
