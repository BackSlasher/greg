# Allows Greg to talk to build servers

import greg.config

class BridgeBuilder:
  def __init__(self, dic):
    pass
  def parse_payload(self, body,headers={},querystring={}):
    pass
  # TODO harden structure (like (job_name, source_repo, source_commit))
  def start_build(self, job_name, params={}):
    pass

def locate_bridge(builder_type):
  if builder_type == 'jenkins':
    import greg.bridge_builder.jenkins
    dic = greg.config.get_config().builders['jenkins']
    return greg.bridge_builder.jenkins.BridgeBuilderJenkins(dic)
  else:
    raise Exception('no such bridge')
