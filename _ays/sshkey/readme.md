
this is the key which can be used in further node.ssh instances.

example how to be used

'''
# creation of a sshkey service, it will be use to access the server
data={}
data['key.priv'] = '' #empty private key trigger auto generation
keyInstance = j.atyourservice.new(name='sshkey',instance="mykey",args=data)
keyInstance.init()
keyInstance.install()
'''

now look at node.ssh how to use this

as command line
'''
ays install -n sshkey -i mykey
'''

if you use interactively just enter an empty string (type '.' and enter) to generate a key.

