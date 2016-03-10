# Allows Greg to talk to build servers

import greg.config

class BridgeBuilder:
  def __init__(self, dic):
    pass
  def parse_payload(self, body,headers={},querystring={}):
    raise NotImplementedError("Please Implement this method")
  # TODO harden structure (like (job_name, source_repo, source_commit))
  def start_build(self, repo, job_name, params={}):
    raise NotImplementedError("Please Implement this method")
  def ensure_webhook(self,job_name,my_url):
    raise NotImplementedError("Please Implement this method")

def locate_bridge(builder_type):
  if builder_type == 'jenkins':
    import greg.builder.jenkins
    dic = greg.config.get_config().builders['jenkins']
    return greg.builder.jenkins.BridgeBuilderJenkins(dic)
  else:
    raise Exception('no such bridge')
