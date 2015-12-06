from JumpScale import j
import os

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):
	def prepare(self,serviceObj):
		"""
		this gets executed before the files are downloaded & installed on approprate spots
		"""
		print('START PROGRAM ............................................\n')
		if not j.do.exists('/opt/jumpscale8/apps/'):
			j.do.createDir('/opt/jumpscale8/apps')
			print('[Create] /opt/jumpscale8/apps')
		else:
			print('[Found] /opt/jumpscale8/apps')
		if not j.do.exists('/opt/jumpscale8/etc/'):
			j.do.createDir('/opt/jumpscale8/etc')
			print('[Create] /opt/jumpscale8/etc')
		else:
			print('[Found] /opt/jumpscale8/etc')
		if not j.do.exists('/opt/jumpscale8/include'):
			j.do.createDir('/opt/jumpscale8/include')
			print('[Create] /opt/jumpscale8/include')
		else:
			print('[Found] /opt/jumpscale8/include')
		if not j.do.exists('/opt/jumpscale8/plugins'):
			j.do.createDir('/opt/jumpscale8/plugins')
			print('[Create] /opt/jumpscale8/plugins')
		else:
			print('[Found] /opt/jumpscale8/plugins')
		if not j.do.exists('/opt/jumpscale8/bin'):
			j.do.createDir('/opt/jumpscale8/bin')
			print('[Create] /opt/jumpscale8/bin')
		else:
			print('[Found] /opt/jumpscale8/bin')
		if not j.do.exists('/opt/jumpscale8/var'):
			j.do.createDir('/opt/jumpscale8/var')
			print('[Create] /opt/jumpscale8/var')
		else:
			print('[Found] /opt/jumpscale8/var')
		if not j.do.exists('/opt/jumpscale8/lib/'):
			j.do.createDir('/opt/jumpscale8/lib')
			print('[Create] /opt/jumpscale8/lib')
		else:
			print('[Found] /opt/jumpscale8/lib')
		return True

	def configure(self,serviceObj):
		tolink = ['ct_run', ' dialyzer', ' epmd', ' erl', ' erlc', ' escript', ' run_erl', ' to_erl', ' typer']
		for link in tolink:
			j.sal.fs.symlink('/opt/jumpscale8/lib/bin/%s' % link, '/opt/jumpscale8/bin/%s' % link, overwriteTarget=True)

#    def stop(self, serviceObj):
#        if not j.sal.process.getPidsByPort(5672):
#            return
#        j.sal.process.execute('cd /opt/jumpscale8/sbin && ./rabbitmqctl stop')	