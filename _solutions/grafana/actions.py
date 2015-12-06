from JumpScale import j
import requests
import json

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def prepare(self, serviceObj):
        j.sal.fs.createDir("/opt/grafana")
        j.sal.fs.createDir("/opt/grafana/conf")
        j.sal.fs.createDir("/opt/grafana/public")

    def configure(self, serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the ays if anything needs to be started
        """
        # influx_instance = serviceObj.hrd.get('param.influxdb.connection')
        if 'influxdb_client' not in serviceObj.producers:
            j.events.opserror_critical(msg="can't find any influxdb_client in the producers", category="grafana.configure")

        # hrd = j.application.getAppInstanceHRD('influxdb_client', influx_instance)
        influxdb_client = serviceObj.producers['influxdb_client'][0]
        host = influxdb_client.hrd.getStr('param.influxdb.client.address')
        port = influxdb_client.hrd.getInt('param.influxdb.client.port')
        login = influxdb_client.hrd.getStr('param.influxdb.client.login')
        passwd = influxdb_client.hrd.getStr('param.influxdb.client.passwd')
        dbname = influxdb_client.hrd.getStr('param.influxdb.client.dbname')

        data = {
          'type': 'influxdb',
          'access': 'proxy',
          'database': dbname,
          'name': 'influxdb_main',
          'url': 'http://%s:%u' % (host, port),
          'user': login,
          'password': passwd,
          'default': True,
        }

        # need to start the grafana backend server to enable http api
        serviceObj.start()

        # check if the datasource already exists
        configured_password = serviceObj.hrd.get('param.password')
        grafanaclient = j.clients.grafana.get(username='admin', password='admin')
        if not grafanaclient.isAuthenticated():
            grafanaclient = j.clients.grafana.get(username='admin', password=configured_password)
        else:
            grafanaclient.changePassword(configured_password)

        datasources = grafanaclient.listDataSources()
        present = False
        for ds in datasources:
            if ds['url'] == data['url'] and ds['user'] == data['user'] and \
               ds['password'] == data['password'] and ds['access'] == data['access']:
               present = True

        if not present:
            # create the datasource for influxdb
            try:
                grafanaclient.addDataSource(data)
            except Exception as e:
                j.events.opserror_critical(e.message)
