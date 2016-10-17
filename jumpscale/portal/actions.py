
def install(job):
    service = job.service
    cuisine = service.executor.cuisine

    cuisine.core.run('touch $binDir/jspython')

    cfg = cuisine.core.file_read('$appDir/portals/main/config.hrd')
    cfg = j.data.hrd.get(content=cfg, prefixWithName=False)
    cuisine.core.file_write('$appDir/portals/main/config.hrd', str(cfg))

    cuisine.core.dir_ensure('$cfgDir/portals')
    cuisine.core.file_link('$appDir/portals/jslib', '$cfgDir/portals/jslib')
    cuisine.core.file_link('$codeDir/github/jumpscale/jumpscale_portal8/apps/portalbase/AYS81', '$appDir/portals/main/base/AYS81')

    cmd = cuisine.core.args_replace('jspython portal_start.py')
    wd = cuisine.core.args_replace('$appDir/portals/main')
    cuisine.processmanager.ensure('portal_%s' % service.name, cmd=cmd, path=wd)


def start(job):
    service = job.service
    cuisine = service.executor.cuisine
    cuisine.processmanager.start('portal_%s' % service.name)


def stop(job):
    service = job.service
    cuisine = service.executor.cuisine
    cuisine.processmanager.stop('portal_%s' % service.name)
