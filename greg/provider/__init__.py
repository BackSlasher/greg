# Allows Greg to talk to code providers
import greg.config

class BridgeProvider:
  def __init__(self, dic):
    pass
  def parse_payload(self, body, headers={}, querystring={}):
    pass
  def post_commit_test(self, organization, name, commit, builder_type, url, result):
    pass
  def post_pr_message(self, organization, name, pr, message):
    pass
  def ensure_webhook(self,organization,name,my_url):
      pass

def locate_bridge(provider_type):
  if provider_type == 'bitbucket':
    import greg.provider.bitbucket
    dic = greg.config.get_config().providers['bitbucket']
    return greg.provider.bitbucket.BridgeProviderBitbucket(dic)
  else:
    raise Exception('no such bridge '+provider_type)

def locate_bridge_by_url(provider_url):
    config = greg.config.get_config()
    provider_name = config.get_provider_by_source(provider_url)
    return locate_bridge(provider_name)

