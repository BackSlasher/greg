# Allows Greg to talk to code providers
import greg.config

class BridgeProvider:
  def __init__(self, dic):
    pass
  # Document type:
  '''
repo:
  provider: X
  orgranization: X
  name: X
event:
  type: X
  pr:
    id: X
    src_branch: X
    dst_branch: X
    same_repo: X # Are the source repo and dest repo of the PR identical
    reviewers: []
    approvers: []
    code_ok: X # Did the code pass validation
  text: X
  --OR--
  changes: []
  '''
  # Should also test querystring['token']
  def parse_payload(self, body, headers={}, querystring={}):
    pass
  # Post the result on a commit.
  # commit is the commit sha
  # builder_type is a string used to identify the reporting builder
  # url is a URL for the builder's result page
  # result is a boolean indicating pass/fail (Allow None for "in progress")?
  def post_commit_test(self, organization, name, commit, builder_type, url, result):
    pass
  def post_pr_message(self, organization, name, pr, message):
    pass
  # Make sure a repo has a greg webhook
  def ensure_webhook(self,organization,name,my_url):
      pass
  # Get all repos in a specific organization
  def list_repos(self,organization):
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

