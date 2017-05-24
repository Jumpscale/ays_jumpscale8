def install(job):
    cuisine = job.service.executor.cuisine
    data = job.service.model.data

    cuisine.apps.zerotier._init()
    cuisine.apps.zerotier.build(reset=data.reinstall, install=True)

def start(job):
    cuisine = job.service.executor.cuisine
    data = job.service.model.data

    cuisine.apps.zerotier.start()
    for network in data.networks:
        cuisine.apps.zerotier.join_network(network)

def stop(job):
    cuisine = job.service.executor.cuisine
    cuisine.apps.zerotier.stop()

