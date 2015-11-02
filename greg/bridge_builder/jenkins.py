#TODO import upper, like `import ..`?

from greg.bridge_builder import BridgeBuilder
import urllib2
import json
import re

class BridgeBuilderJenkins(BridgeBuilder):
  def parse_repo(self, git_url):
    (raw_pro,no_pro) = git_url.split(':')
    provider_url = re.sub('^git@','',raw_pro)
    (organization,repo_name)=re.sub('\.git$','', no_pro).split('/')
    return [provider_url, organization, repo_name]

  def __init__(self, dic):
    self.url = dic['url']
    self.username = dic['username']
    self.password = dic['password']
    self.incoming_token = dic['incoming_token']

  def parse_payload(self, body,params={}):
    # Verify token
    presented_token=params['token']
    if self.incoming_token != presented_token: raise Exception('Bad token')
    body=json.loads(body)
    job_name=body['name']
    job_done=(body['build']['phase'] == 'COMPLETED')
    [provider, org, repo_name] = self.parse_repo(body['build']['parameters']['SOURCE'])
    job_good = ( body['build']['status']=='SUCCESS' or body['build']['status']=='UNSTABLE' )
    commit=body['build']['parameters']['COMMIT']
    context=body['build']['parameters']['CONTEXT'] # TODO not actually implemented with us, should be used to indicate whether this is a test/merge
    return {
        'name': job_name,
        'done': job_done,
        'good': job_good,
        'source': {
          'provider': provider,
          'organization': org,
          'name': repo_name,
          'commit': commit,
          },
        }
