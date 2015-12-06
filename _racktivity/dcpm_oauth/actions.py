from JumpScale import j
import configparser

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    """
    process for install
    -------------------
    step1: prepare actions
    step2: check_requirements action
    step3: download files & copy on right location (hrd info is used)
    step4: configure action
    step5: check_uptime_local to see if process stops  (uses timeout $process.stop.timeout)
    step5b: if check uptime was true will do stop action and retry the check_uptime_local configureheck
    step5c: if check uptime was true even after stop will do halt action and retry the check_uptime_local check
    step6: use the info in the hrd to start the application
    step7: do check_uptime_local to see if process starts
    step7b: do monitor_local to see if package healthy installed & running
    step7c: do monitor_remote to see if package healthy installed & running, but this time test is done from central location
    """

    def configure(self, serviceObj):
        config = configparser.RawConfigParser()
        config.add_section('main')
        config.set('main', 'baseuri', serviceObj.hrd.get("param.singlesignon.baseuri"))
        
        config.add_section('provider.singlesignon')
        config.set('provider.singlesignon', 'url', serviceObj.hrd.get("param.singlesignon.url"))
        config.set('provider.singlesignon', 'token_url', serviceObj.hrd.get("param.singlesignon.token_url"))
        config.set('provider.singlesignon', 'logout_url', serviceObj.hrd.get("param.singlesignon.logout_url"))
        config.set('provider.singlesignon', 'client_id', serviceObj.hrd.get("param.singlesignon.client_id"))
        config.set('provider.singlesignon', 'client_secret', serviceObj.hrd.get("param.singlesignon.client_secret"))
        
        config.add_section('singlesignon.args')
        config.set('singlesignon.args', 'scope', serviceObj.hrd.get("param.singlesignon.scope"))
        config.set('singlesignon.args', 'response_type', serviceObj.hrd.get("param.singlesignon.response_type"))
        
        with open('/opt/qbase5/pyapps/dcpm/cfg/auth_oauth2.cfg', 'wb') as configfile:
            config.write(configfile)