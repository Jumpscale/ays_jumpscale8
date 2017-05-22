def install(job):
    cuisine = job.service.executor.cuisine

    cuisine.core.run("apt-get update")
    cuisine.apps.odoo.build()
    cuisine.apps.odoo.install()
    # Install ERPpeek Library to enable creating/modifying odoo databases easily
    cuisine.core.run("pip2 install erppeek")
    start(job)
    args = {
        'company_name': job.service.model.data.company,
        'username': job.service.model.data.username,
        'password': job.service.model.data.password,
    }
    cmd = """
    import erppeek
    client = erppeek.Client('http://localhost:8069')
    client.create_database("admin", "{company_name}")
    client.install('l10n_be')
    client.install('account_accountant')
    company_model = client.model('res.company')
    users_model = client.model('res.users')
    erppeek.Record(company_model, 1).write({{'name': "{company_name}"}})
    erppeek.Record(users_model, 1).write({{'login': "{username}", 'password': "{password}"}})
    """
    cmd = cmd.format(**args)
    cuisine.core.execute_script(cmd, interpreter="python2", showout=True, tmux=False)


def start(job):
    name = 'odoo_{0}'.format(job.service.name)
    cuisine = job.service.executor.cuisine
    if not cuisine.apps.postgresql.isStarted():
        cuisine.apps.postgresql.start()
    cmd = """
     cd $BINDIR
     sudo -H -u odoo \
     PATH=$PATH \
     PYTHONPATH=$JSLIBEXTDIR:$PYTHONPATH \
     LD_LIBRARY_PATH=$LIBDIR/postgres/:$LD_LIBRARY_PATH \
     ./odoo-bin --addons-path=$JSLIBEXTDIR/odoo-addons,$JSLIBEXTDIR/odoo/addons/ --db-template=template0
     """
    cuisine.processmanager.ensure(name=name, cmd=cmd)


def stop(job):
    name = 'odoo_{0}'.format(job.service.name)
    cuisine = job.service.executor.cuisine
    cuisine.processmanager.stop(name=name)
