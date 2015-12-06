from JumpScale import j
import os

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):
	def prepare(self,serviceObj):
		"""
		this gets executed before the files are downloaded & installed on approprate spots
		"""
		print('START PROGRAM ............................................\n')
		folders = ['bin', 'include', 'lib', 'share']
		for folder in folders:
			if not j.do.exists('/opt/jumpscale8/%s' % folder):
				j.do.createDir('/opt/jumpscale8/%s' %folder)
				print('[Create] /opt/jumpscale8/%s)' % folder)
			else:
				print('[Found] /opt/jumpscale8/%s)' % folder)
		return True

#	def configure(self,serviceObj):

#    def stop(self, serviceObj):
#        if not j.sal.process.getPidsByPort(5672):
#            return
#        j.sal.process.execute('cd /opt/jumpscale8/sbin && ./rabbitmqctl stop')	
