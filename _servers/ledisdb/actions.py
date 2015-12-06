from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

class Actions(ActionsBase):
    """
    process for install
    -------------------
    step1: prepare actions
    step2: check_requirements action
    step3: download files & copy on right location (hrd info is used)
    step4: configure action
    step5: check_uptime_local to see if process stops  (uses timeout $process.stop.timeout)
    step5b: if check uptime was true will do stop action and retry the check_uptime_local check
    step5c: if check uptime was true even after stop will do halt action and retry the check_uptime_local check
    step6: use the info in the hrd to start the application
    step7: do check_uptime_local to see if process starts
    step7b: do monitor_local to see if package healthy installed & running
    step7c: do monitor_remote to see if package healthy installed & running, but this time test is done from central location
    """

    def prepare(self,serviceObj):
        """
        """
        pass


    def configure(self,serviceObj):
        """
        """
        pass

    def removedata(self,serviceObj):
        j.do.delete("/opt/code/github/siddontang/",force=True)
        j.do.delete("/opt/code/github/facebook/rocksdb/",force=True)
        j.do.delete("/opt/build/ledisdb",force=True)
        j.do.delete("/opt/ledisdb",force=True)


    def build(self,serviceObj):     

        #to reset the state use ays reset -n ...
        params = {'ledis' :"/opt/build/git.aydo.com/aydo/ledisdb"}

        def preparebuild():
            j.sal.ubuntu.checkInstall(["cmake"], "cmake")
            j.sal.ubuntu.checkInstall(["gcc"], "gcc")

            cmd='apt-get install --no-install-recommends -y ca-certificates curl git-core g++ dh-autoreconf pkg-config libgflags-dev liblua5.1-dev git tmux mercurial'
            j.do.executeInteractive(cmd)

        j.actions.start(retry=2, name="preparebuild",description='', cmds='', action=preparebuild, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=False, serviceObj=serviceObj)

        #WAS QUITE UGLY, COPY PASTE FROM BASH FILES. DID SOME CLEANUP ALREADY (KRISTOF)
        #ALSO THE WAY HOW WE COMPILED IN NON SANDBOXED DIRS IS UGLY, NOW MOVED IT TO SANDBOXED DIRS
        #MORE JUMPSCALE PRIMITIVES SHOULD BE USED
        #ALL THE GIT CHECKOUTS SHOULD HAVE BEEN DONE AS PART OF THE JP.HRD (the code recipe) & then copy to a build directory (see what we did for luajit_build), ALSO FIXED

        # Get and compile :
        #   - snappy
        #   - add leveldb for good measure
        #   - for gflags and lua


        cmd="""
set -e
# bail if anywhere in there
# SNAPPY
cd /opt/build/github.com/siddontang/snappy/
export SNAPPY_DIR=%(ledis)s
autoreconf --force --install
./configure --prefix=$SNAPPY_DIR
make
make install
""" % params
        j.actions.start(retry=1, name="snappy",description='compile snappy', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)


        cmd="""
set -e
cd /opt/build/github.com/facebook/rocksdb/
# git checkout -b 3.5.fb origin/3.5.fb
make shared_lib
cp librocksdb.so %(ledis)s/lib
cp -r include %(ledis)s 
""" % params
        j.actions.start(retry=1, name="ROCKSDB",description='compile ROCKSDB', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)

        cmd="""
# LEVELDB
set -e
cd /opt/build/github.com/siddontang/leveldb/
export LEVELDB_DIR=%(ledis)s
export SNAPPY_DIR=%(ledis)s
echo "echo \"PLATFORM_CFLAGS+=-I$SNAPPY_DIR/include\" >> build_config.mk" >> build_detect_platform
echo "echo \"PLATFORM_CXXFLAGS+=-I$SNAPPY_DIR/include\" >> build_config.mk" >> build_detect_platform
echo "echo \"PLATFORM_LDFLAGS+=-L $SNAPPY_DIR/lib -lsnappy\" >> build_config.mk" >> build_detect_platform
make SNAPPY=1
mkdir -p $LEVELDB_DIR/include/leveldb
install include/leveldb/*.h $LEVELDB_DIR/include/leveldb
mkdir -p $LEVELDB_DIR/lib
cp -P libleveldb.* $LEVELDB_DIR/lib
# ln -s /usr/local/leveldb/lib/libleveldb.so.1 /usr/lib/libleveldb.so.1
""" % params
        j.actions.start(retry=1, name="LEVELDB",description='compile LEVELDB', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)
        #@todo is not working, still issue

        #is now embedded below in this action file
        # #copy our dev.sh file from ledisdb repo
        # src="/opt/code/git/binary/ledisdb/build/dev.sh"
        # dest="/opt/build/ledisdb/ledisdb/dev.sh"
        # j.do.copyFile(src,dest)

        cmd="""
set -ex
. /opt/go/goenv.sh
cd /opt/go/myproj

go get github.com/tools/godep

"""

        j.actions.start(retry=1, name="godeps",description='get godeps', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)

        cmd="""
set -ex

export LEDISROOT="/opt/build/ledisdb/ledisdb/"

export GOPATH=/opt/go/myproj:$LEDISROOT
export GOROOT=/opt/go
export PATH=$GOROOT/bin:$GOROOT/myproj/bin:$PATH

#default snappy and leveldb install path
#you may change yourself
SNAPPY_DIR=%(ledis)s
LEVELDB_DIR=%(ledis)s
ROCKSDB_DIR=%(ledis)s
LUA_DIR=%(ledis)s

GO_BUILD_TAGS=
CGO_CFLAGS=
CGO_CXXFLAGS=
CGO_LDFLAGS=

#get lua5.1 from build dir
cp %(ledis)s/lua/* %(ledis)s/lib
# check dependent libray, now we only check simply, maybe later add proper checking 

# check snappy 
if [ -f $SNAPPY_DIR/include/snappy.h ]; then
    echo 1
    CGO_CFLAGS="$CGO_CFLAGS -I$SNAPPY_DIR/include"
    CGO_CXXFLAGS="$CGO_CXXFLAGS -I$SNAPPY_DIR/include"
    CGO_LDFLAGS="$CGO_LDFLAGS -L$SNAPPY_DIR/lib -lsnappy"
    LD_LIBRARY_PATH="$SNAPPY_DIR/lib"
    DYLD_LIBRARY_PATH="$SNAPPY_DIR/lib"
fi

# check leveldb
if [ -f $LEVELDB_DIR/include/leveldb/c.h ]; then
    echo 2
    CGO_CFLAGS="$CGO_CFLAGS -I$LEVELDB_DIR/include"
    CGO_CXXFLAGS="$CGO_CXXFLAGS -I$LEVELDB_DIR/include"
    CGO_LDFLAGS="$CGO_LDFLAGS -L$LEVELDB_DIR/lib -lleveldb"
    LD_LIBRARY_PATH="$LEVELDB_DIR/lib"
    DYLD_LIBRARY_PATH="$DYLD_LIBRARY_PATH"
    GO_BUILD_TAGS="$GO_BUILD_TAGS leveldb"
fi

# check rocksdb
if [ -f $ROCKSDB_DIR/include/rocksdb/c.h ]; then
    echo 3
    CGO_CFLAGS="$CGO_CFLAGS -I$ROCKSDB_DIR/include"
    CGO_CXXFLAGS="$CGO_CXXFLAGS -I$ROCKSDB_DIR/include"
    CGO_LDFLAGS="$CGO_LDFLAGS -L$ROCKSDB_DIR/lib -lrocksdb"
    LD_LIBRARY_PATH="$ROCKSDB_DIR/lib"
    DYLD_LIBRARY_PATH="$ROCKSDB_DIR/lib"
    GO_BUILD_TAGS="$GO_BUILD_TAGS rocksdb"
fi


#check lua
if [ -f $LUA_DIR/include/lua.h ]; then
    echo 4
    CGO_CFLAGS="$CGO_CFLAGS -I$LUA_DIR/include"
    CGO_LDFLAGS="$CGO_LDFLAGS -L$LUA_DIR/lib -llua"
    LD_LIBRARY_PATH="$LUA_DIR/lib"
    DYLD_LIBRARY_PATH="$LUA_DIR/lib"
    GO_BUILD_TAGS="$GO_BUILD_TAGS lua"
fi

# export CGO_CFLAGS
# export CGO_CXXFLAGS
# export CGO_LDFLAGS
# export LD_LIBRARY_PATH
# export DYLD_LIBRARY_PATH
# export GO_BUILD_TAGS

echo "GO BUILD TAGS:$GO_BUILD_TAGS"

#I read about bug to use other version (but does not resolve my issue)
#cd /opt/go/myproj/src/github.com/syndtr/goleveldb/leveldb
#git checkout 871eee0a7546bb7d1b2795142e29c4534abc49b3
#cd /opt/go/myproj
#go build github.com/syndtr/goleveldb/leveldb

#build dir needs to be under goroot
mkdir -p /opt/go/myproj/src/github.com/siddontang/
cp -R /opt/build/github.com/siddontang/ledisdb /opt/go/myproj/src/github.com/siddontang/
cd /opt/go/myproj/src/github.com/siddontang/ledisdb/
godep restore
make
make test

""" % params
        j.actions.start(retry=1, name="ledisdb",description='compile ledisdb', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)

        def copyBins():
            gobin = "/opt/go/myproj/bin"
            destfolder = "/opt/code/git/binary/ledisdb/bin"
            j.sal.fs.removeDirTree(destfolder)
            j.sal.fs.createDir(destfolder)
            for file_ in j.sal.fs.find(gobin, "ledis*"):
                j.sal.fs.copyFile(j.sal.fs.joinPaths(gobin, file_), destfolder)

        j.actions.start(retry=1, name="package",description='copy resuls', action=copyBins, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceObj)

        def cleanup():
            todelete=["$(param.base.luajit)/include/","$(param.base.luajit)/lib/luarocks/","$(param.base.luajit)/lib/pkgconfig/","$(param.base.luajit)/share/cmake/","$(param.base.luajit)/share/man/"]
            for item in todelete:
                j.do.delete(item)
        # j.actions.start(retry=1, name="cleanup",description='', cmds="", action=cleanup, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=False, serviceObj=serviceObj)
