#TODO import upper, like `import ..`?

from greg.builder import BridgeBuilder
import greg.config
import requests
import json
import re

class BridgeBuilderJenkins(BridgeBuilder):
  def parse_repo(self, git_url):
    if '@' in git_url:
      # SSH
      (raw_pro,no_pro) = git_url.split(':')
      provider_url = raw_pro+':'
      (organization,repo_name)=re.sub('\.git$','', no_pro).split('/')
      return [provider_url, organization, repo_name]
    else:
      # TODO support https sources
      raise Exception('Source configuration not supported')

  def __init__(self, dic):
    self.url = dic['url']
    self.username = dic['username']
    self.password = dic['password']
    self.incoming_token = dic['incoming_token']

  def parse_payload(self, body,headers={},querystring={}):
    # Verify token
    presented_token=querystring['token']
    if self.incoming_token != presented_token: raise Exception('Bad token')
    body=json.loads(body)
    job_name=body['name']
    job_done=(body['build']['phase'] == 'COMPLETED')
    [provider_url, org, repo_name] = self.parse_repo(body['build']['parameters']['SOURCE'])
    job_good = ( body['build']['status']=='SUCCESS' or body['build']['status']=='UNSTABLE' )
    commit=body['build']['parameters']['COMMIT']
    context=body['build']['parameters']['CONTEXT'] # TODO not actually implemented with us, should be used to indicate whether this is a test/merge
    job_report=body['build']['parameters']['REPORT']=='true'
    # Optional values
    job_pr=body['build']['parameters'].get('PR',None)
    job_target=body['build']['parameters'].get('TARGET',None)
    job_url=body['build']['full_url']
    return {
        'name': job_name,
        'done': job_done,
        'good': job_good,
        'report': job_report,
        'pr': job_pr,
        'context': context,
        'source': {
          'provider_url': provider_url,
          'organization': org,
          'name': repo_name,
          'commit': commit,
          },
        'target': job_target,
        'url': job_url,
        }

  def start_build(self, repo, job_name, params={}):
    url = '%s/job/%s/buildWithParameters' % (self.url,job_name)
    # Mix source in params
    # 'SOURCE'
    git_source_base = greg.config.get_config().provider_source(repo['provider'])
    git_source = '%s%s/%s.git' % (git_source_base,repo['organization'],repo['name'])
    params['SOURCE']=git_source
    resp = requests.request(url=url, method='POST', params=params, auth=(self.username, self.password))
    resp.raise_for_status() # Raise error in case it fails
