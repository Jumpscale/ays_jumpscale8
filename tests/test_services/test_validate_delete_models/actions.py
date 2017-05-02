def init_actions_(service, args):

    """

    this needs to returns an array of actions representing the depencies between actions.

    Looks at ACTION_DEPS in this module for an example of what is expected

    """
    # some default logic for simple actions
    return {

        'test': ['install']

    }


def test(job):
    """
    Tests parsing of a bp with/without default values
    """
    import sys
    import json
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    repos = []
    repo_name = 'sample_repo_delete_models'
    bp_name = 'validate_delete_model_sample.yaml'
    try:
        ays_client = j.clients.atyourservice.get()
        execute_bp_res = ays_client.api.ays.executeBlueprint(data={}, blueprint=bp_name, repository=repo_name)
        if execute_bp_res.status_code == 200:
            repo_info = json.loads(ays_client.api.ays.getRepository(repo_name).text)
            ays_client.api.ays.destroyRepository(data={}, repository=repo_name)
            if j.sal.fs.exists(j.sal.fs.joinPaths(repo_info['path'], "actors")):
                failures.append('Actors directory is not deleted')
            if j.sal.fs.exists(j.sal.fs.joinPaths(repo_info['path'], "services")):
                failures.append('Services directory is not deleted')
            if j.core.jobcontroller.db.runs.find(repo=repo_info['path']):
                failures.append('Jobs are not deleted after repository destroy')
        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)

    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        for repo in repos:
            ays_client.api.ays.destroyRepository(data={}, repository=repo)
