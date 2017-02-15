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
    Tests dependency tree
    """
    import sys
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    try:
        # Tests parent relationship
        if job.service.name == 'parent':
            # make sure service has only one parent
            if job.service.parent.name != 'cockpit':
                model.data.result = RESULT_FAILED % ("Service has the wrong parent")
            elif model.dbobj.actorName not in job.service.parent.consumers:
                # validate that the current service is added as a consumers of the parent
                model.data.result = RESULT_FAILED % ("Current service is not added in the consumers list of the parent")

        if job.service.name == 'consumers':
            if 'vdc' not in job.service.producers:
                model.data.result =  RESULT_FAILED % ("vdc is not added to producers")
            elif 'g8client' not in job.service.producers:
                model.data.result = RESULT_FAILED % ("g8client is not in producers")
            elif len(job.service.producers['g8client']) != 3:
                model.data.result = RESULT_FAILED % ("Wrong number of g8client producers") 
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])

    job.service.save()