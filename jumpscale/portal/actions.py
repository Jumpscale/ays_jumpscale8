
def install(job):
    service = job.service
    cuisine = service.executor.cuisine

    cfg = cuisine.core.file_read('$appDir/portals/main/config.hrd')
    cfg = j.data.hrd.get(content=cfg, prefixWithName=False)
    cuisine.core.file_write('$appDir/portals/main/config.hrd', str(cfg))

    cuisine.core.dir_ensure('$cfgDir/portals')
    cuisine.core.file_link('$appDir/portals/jslib', '$cfgDir/portals/jslib')
    cuisine.core.file_link('$codeDir/github/jumpscale/jumpscale_portal8/apps/portalbase/AYS81', '$appDir/portals/main/base/')

    cmd = cuisine.core.args_replace('jspython portal_start.py')
    wd = cuisine.core.args_replace('$appDir/portals/main')
    pm = cuisine.processmanager.get('tmux')
    pm.ensure('portal_%s' % service.name, cmd=cmd, path=wd)


def start(job):
    service = job.service
    cuisine = service.executor.cuisine
    pm = cuisine.processmanager.get('tmux')
    pm.start('portal_%s' % service.name)


def stop(job):
    service = job.service
    cuisine = service.executor.cuisine
    pm = cuisine.processmanager.get('tmux')
    pm.stop('portal_%s' % service.name)
