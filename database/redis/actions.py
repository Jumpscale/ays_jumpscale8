def install(job):
    service = job.service
    cuisine = service.executor.cuisine

    cuisine.core.run('touch $binDir/redis-server')
    cuisine.apps.redis.install()
    cuisine.apps.redis.start(
        name=service.name,
        ip=service.model.data.host,
        port=service.model.data.port,
        maxram=service.model.data.maxram,
        appendonly=service.model.data.appendonly)


def start(job):
    service = job.service
    cuisine = service.executor.cuisine

    cuisine.apps.redis.install()
    cuisine.apps.redis.start(
        name=service.name,
        ip=service.model.data.host,
        port=service.model.data.port,
        maxram=service.model.data.maxram,
        appendonly=service.model.data.appendonly)


def stop(job):
    cuisine.apps.redis.stop(job.service.name)
