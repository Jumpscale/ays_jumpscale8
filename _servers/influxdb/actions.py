from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()

CONFIG="""
reporting-disabled = false

[meta]
  dir = "$vardir/influxdb/meta"
  hostname = "localhost"
  bind-address = ":8088"
  retention-autocreate = true
  election-timeout = "1s"
  heartbeat-timeout = "1s"
  leader-lease-timeout = "500ms"
  commit-timeout = "50ms"
  cluster-tracing = false

[data]
  dir = "$vardir/influxdb/data"
  engine = "bz1"
  max-wal-size = 104857600
  wal-flush-interval = "10m0s"
  wal-partition-flush-delay = "2s"
  wal-dir = "$vardir/influxdb/wal"
  wal-logging-enabled = true
  wal-ready-series-size = 30720
  wal-compaction-threshold = 0.5
  wal-max-series-size = 1048576
  wal-flush-cold-interval = "5s"
  wal-partition-size-threshold = 20971520

[cluster]
  force-remote-mapping = false
  write-timeout = "5s"
  shard-writer-timeout = "5s"
  shard-mapper-timeout = "5s"

[retention]
  enabled = true
  check-interval = "10m0s"

[shard-precreation]
  enabled = true
  check-interval = "10m0s"
  advance-period = "30m0s"

[admin]
  enabled = true
  bind-address = ":8083"
  https-enabled = false
  https-certificate = "/etc/ssl/influxdb.pem"

[monitor]
  store-enabled = false
  store-database = "_internal"
  store-interval = "10s"

[http]
  enabled = true
  bind-address = ":8086"
  auth-enabled = false
  log-enabled = true
  write-tracing = false
  pprof-enabled = false
  https-enabled = false
  https-certificate = "/etc/ssl/influxdb.pem"

[collectd]
  enabled = false
  bind-address = ":25826"
  database = "collectd"
  retention-policy = ""
  batch-size = 1000
  batch-pending = 5
  batch-timeout = "10s"
  typesdb = "/usr/share/collectd/types.db"

[opentsdb]
  enabled = false
  bind-address = ":4242"
  database = "opentsdb"
  retention-policy = ""
  consistency-level = "one"
  tls-enabled = false
  certificate = "/etc/ssl/influxdb.pem"
  batch-size = 1000
  batch-pending = 5
  batch-timeout = "1s"

[continuous_queries]
  log-enabled = true
  enabled = true
  recompute-previous-n = 2
  recompute-no-older-than = "10m0s"
  compute-runs-per-interval = 10
  compute-no-more-than = "2m0s"

[hinted-handoff]
  enabled = true
  dir = "/root/.influxdb/hh"
  max-size = 1073741824
  max-age = "168h0m0s"
  retry-rate-limit = 0
  retry-interval = "1s"

"""


class Actions(ActionsBase):

    def prepare(self,serviceObj):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """

        if j.do.TYPE.lower().startswith("osx"):
            res=j.do.execute("brew install influxdb")
            res=j.do.execute("brew list influxdb")
            for line in res[1].split("\n"):
                if line.strip()=="":
                    continue
                if j.do.exists(line.strip()) and line.find("bin/")!=-1:
                    destpart=line.split("bin/")[-1]
                    dest="/opt/influxdb//%s"%destpart
                    j.sal.fs.createDir(j.sal.fs.getDirName(dest))
                    j.do.copyFile(line,dest)
                    j.do.chmod(dest, 0o770) 

        if j.do.TYPE.lower().startswith("ubuntu64"):
            j.sal.ubuntu.downloadInstallDebPkg("https://s3.amazonaws.com/influxdb/influxdb_0.9.4.2_amd64.deb",minspeed=50)
            for path in j.sal.ubuntu.listFilesPkg("influxdb",regex=".*\/versions\/.*\/infl.*"):
                #find the files which have been installed
                j.do.copyFile(path,"/opt/influxdb/",skipIfExists=True)            

        return True

    def configure(self, service):
        cfg = j.dirs.replaceTxtDirVars(CONFIG, additionalArgs={})
        j.do.writeFile("/opt/influxdb//cfg/config.toml", cfg)

    def build(self,serviceObj):

        #to reset the state use ays reset -n ...

        j.sal.ubuntu.check()
        #@todo