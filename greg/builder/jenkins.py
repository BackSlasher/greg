#TODO import upper, like `import ..`?

from greg.builder import BridgeBuilder
import greg.config
import requests
import json
import re
import xml.etree.ElementTree as ET

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
    job_good = body['build'].get('status','UNKNOWN') in ['SUCCESS', 'UNSTABLE']
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

  def get_job_config(self,job_name):
    url = '%s/job/%s/config.xml' % (self.url,job_name)
    resp = requests.request(url=url, method='GET', auth=(self.username, self.password))
    resp.raise_for_status()
    config = ET.fromstring(resp.text)
    return config

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

  def ensure_notification_endpoint(self,my_url,job_config):

    notification_container_name = 'com.tikal.hudson.plugins.notification.HudsonNotificationProperty'
    if job_config.find('properties').find(notification_container_name) is None:
        ET.SubElement(job_config.find('properties'),notification_container_name)
    if job_config.find('properties').find(notification_container_name).find('endpoints') is None:
        ET.SubElement(job_config.find('properties').find(notification_container_name),'endpoints')

    notification_endpoints = job_config.find('properties').find(notification_container_name).find('endpoints')
    # Find endpoint matching our url. If none, create one
    endpoint_element_name = 'com.tikal.hudson.plugins.notification.Endpoint'
    endpoints = notification_endpoints.findall(endpoint_element_name)
    # Filter down to our endpoints
    endpoints = [ e for e in endpoints if self.url_base_compare(e.find('url').text,my_url) ]
    #TODO more intelligent handling of endpoint
    # Remove current endpoints
    for e in endpoints:
        notification_endpoints.remove(e)
    # Create new endpoint
    new_endpoint = ET.SubElement(notification_endpoints,endpoint_element_name)
    def add_mini_element(parent,name,value):
        res = ET.SubElement(parent,name)
        res.text=value
        return res

    add_mini_element(new_endpoint,'protocol','HTTP')
    add_mini_element(new_endpoint,'format','JSON')
    add_mini_element(new_endpoint,'url',my_url)
    add_mini_element(new_endpoint,'event','completed')
    add_mini_element(new_endpoint,'timeout','30000')
    add_mini_element(new_endpoint,'loglines','0')


  def ensure_webhook(self,job_name,my_url):
    # Required permissions:
    # strategy.add(Jenkins.READ,it)
    # strategy.add(Job.CONFIGURE,it)
    # strategy.add(Job.READ,it)

    # Get XML
    config = self.get_job_config(job_name)
    # Make sure parameters are exactly what we need
    #TODO complete
    # Make sure we have at least one endpoint pointing to greg's url
    self.ensure_notification_endpoint(my_url,config)
    # Job completed
