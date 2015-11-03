# Allows Greg to talk to code providers

import greg.config

class BridgeProvider:
  def __init__(self, dic):
    pass
  def parse_payload(self, body, params={}):
    pass
  def post_commit_test(self, organization, name, commit, builder_type, url, result):
    pass
  def post_pr_message(self, organization, name, pr, message):
    pass

def locate_bridge(provider_type):
  if provider_type == 'bitbucket':
    import greg.bridge_provider.bitbucket
    dic = greg.config.get_config().providers['bitbucket']
    return greg.bridge_provider.bitbucket.BridgeProviderBitbucket(dic)
  else:
    raise Exception('no such bridge')

def locate_bridge_by_url(provider_url):
    if provider_url.startswith('http://bitbucket.org'):
        return locate_bridge('bitbucket')

