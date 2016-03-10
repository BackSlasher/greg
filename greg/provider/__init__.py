# Allows Greg to talk to code providers
import greg.config

class BridgeProvider(object):
  def __init__(self, dic):
    pass
  # Document type:
  '''
repo:
  provider: X
  orgranization: X
  name: X
event:
  type: X # 'pr:comment' / 'push'
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
    raise NotImplementedError("Please Implement this method")
  # Post the result on a commit.
  # commit is the commit sha
  # builder_type is a string used to identify the reporting builder
  # url is a URL for the builder's result page
  # result is a boolean indicating pass/fail (Allow None for "in progress")?
  def post_commit_test(self, organization, name, commit, builder_type, url, result):
    raise NotImplementedError("Please Implement this method")
  def post_pr_message(self, organization, name, pr, message):
    raise NotImplementedError("Please Implement this method")
  # Make sure a repo has a greg webhook
  def ensure_webhook(self,organization,name,my_url):
    raise NotImplementedError("Please Implement this method")
  # Get all repos in a specific organization
  def list_repos(self,organization):
    raise NotImplementedError("Please Implement this method")

  def url_base_compare(self,a,b):
    def strip_url(u):
      u=u._replace(path='')
      u=u._replace(query='')
      u=u._replace(fragment='')
      return u
    from urlparse import urlparse
    u_a = strip_url(urlparse(a))
    u_b = strip_url(urlparse(b))
    return u_a == u_b


def locate_bridge(provider_type):
  if provider_type == 'bitbucket':
    import greg.provider.bitbucket
    dic = greg.config.get_config().providers['bitbucket']
    return greg.provider.bitbucket.BridgeProviderBitbucket(dic)
  elif provider_type == 'github':
    import greg.provider.github
    dic = greg.config.get_config().providers['github']
    return greg.provider.github.BridgeProviderGithub(dic)
  else:
    raise Exception('no such bridge '+provider_type)

def locate_bridge_by_url(provider_url):
    config = greg.config.get_config()
    provider_name = config.get_provider_by_source(provider_url)
    return locate_bridge(provider_name)

