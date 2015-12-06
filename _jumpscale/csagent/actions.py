from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

import os.path

def log(message):
    print((' :: ' + message))


class Actions(ActionsBase):


    def build(self,serviceObj):
    
        # ays is responsible for pulling the source code and putting it here
        BUILD_BASE = '/opt/build/github.com/Jumpscale/csagent/'

        LUAROCKS_COMMAND = '/opt/luajit/bin/luarocks --server=http://rocks.moonscript.org/manifests/amrhassan'

        def lua_deps():
            """Returns an array of Lua module dependencies that need to be retrieved from MoonRocks"""
            deps = open(os.path.join(BUILD_BASE, 'dependencies.txt')).read().split()
            deps.remove('lunix')    # Bad package. Uninstallable via LuaRocks
            return deps
            
        def install_lunix():
            LUNIX_BUILD_BASE = '/opt/build/github.com/wahern/lunix'  # It is put there by ays before doing the build 
            LUA_PREFIX = '/opt/luajit'
            command = 'cd %(build_base)s ; make all prefix=%(prefix)s ; make install prefix=%(dest_prefix)s' %{'build_base': LUNIX_BUILD_BASE, 'prefix': LUA_PREFIX, 'dest_prefix': os.path.join(BUILD_BASE, 'deps')}
            log('Installing lunix')
            j.do.execute(command)

        def install_lua_deps():
            for dep in lua_deps():
                install_command = '%(luarocks_command)s install --tree=%(local_tree_path)s %(dep)s' % {
                    'luarocks_command': LUAROCKS_COMMAND, 
                    'local_tree_path': os.path.join(BUILD_BASE, 'deps'), 
                    'dep': dep}
            
                log('Installing ' + dep)
                j.do.execute(install_command) 

        install_lunix()
        install_lua_deps()

        # TODO: Apply the patches in `build_patches` to /opt/csagent/deps/
