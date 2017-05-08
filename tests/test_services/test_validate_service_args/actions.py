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
    Test the created directory structure is corrected after ays blueprint on a test repo
    """
    import sys
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    blueprints = {
        'bp_args_with_dot.yaml': True,
        'bp_args_with_underscore.yaml': True,
        'bp_valid_args.yaml': True,
        'bp_non_exists_args.yaml': False,
    }
    repo = None

    try:
        repo = 'sample_repo4'
        cl = j.clients.atyourservice.get().api.ays
        for bp_name, should_success in blueprints.items():
            try:
                bp_resp = cl.executeBlueprint(data=None, repository=repo, blueprint=bp_name)
                if not should_success and bp_resp.status_code == 200:
                    failures.append("blueprint %s should have failed" % bp_name)
            except Exception as e:
                if should_success:
                    failures.append("blueprint %s should have succeded : %s" % (bp_name, str(e)))

        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)

    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        if repo:
            cl.destroyRepository(data=None, repository=repo)
