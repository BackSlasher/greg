
from greg.bridge_provider import BridgeProvider
import requests
import json

class BridgeProviderBitbucket(BridgeProvider):

  def api_raw(self,url,form_data={},method=None,request_type=None):
    headers={}
    if (method is None):
      if form_data == {}: method='GET'
      else: method='POST'
    data=None
    if request_type is None:
      if form_data is not None: data=form_data
    elif request_type == 'json':
      headers['content-type']='application/json'
      data=json.dumps(form_data)
    elif request_type == 'string':
      data=form_data
    else:
      raise Exception("Bad request_type"%(request_type))
    resp=requests.request(method=method, url=url, data=data, headers=headers, auth=(self.username, self.password))
    resp.raise_for_status() # raise error if there's an issue
    body = resp.text
    if resp.headers['content-type'] == 'application/json':
      body = json.loads(body)
    return body

  def api(self,version,path,form_data={},method=None,request_type=None):
    uri="https://api.bitbucket.org/%d/%s" %(version,path)
    return self.api_raw(uri,form_data,method,request_type)

  def get_pr_json(self, organization, name, pr_id):
    return self.api('2.0',"repositories/%s/%s/pullrequests/%s" %(organization, name, pr_id))

  def get_commit_json(self, organization, name, commit):
    return self.api('2.0',"repositories/%s/%s/commit/%s" %(organization, name, commit))

  def commit_code_ok(self, organization, name, commit):
      commit = self.get_commit_json(organization, name, commit)
      return any(p['approved'] and p['user']['username']==self.username for p in commit['participants']) #TODO handle cases where email is provided instead of username

  def post_commit_comment(self,organization,name,commit,content):
      return self.api('1.0',"repositories/%s/%s/changesets/%s/comments"%(organization, name, commit),{'content': content},'post')

  def post_pr_comment(self,organization,name,pr_id,content):
      return self.api('1.0',"repositories/%s/%s/pullrequests/%s/comments"%(organization, name, pr_id),{'content': content},'post')

  def set_commit_approval(self,organization,name,commit,is_approved):
      return self.api('2.0',"repositories/%s/%s/commit/%s/approve"%(organization, name, commit),method=( 'post' if is_approved else 'delete'))

  def __init__(self, dic):
    self.username=dic['username']
    self.password=dic['password']
    self.incoming_token=dic['incoming_token']

  def parse_payload(self, body, params={}):
    method=params['X_EVENT_KEY'] # request.env['HTTP_X_EVENT_KEY']
    # Can be either pullrequest:comment_created or repo:push
    body = json.loads(body)
    repo_org = body['repository']['owner']['username']
    repo_name = body['repository']['name']
    ret = {
        'repo': {
          'provider': 'bitbucket',
          'organization': repo_org,
          'name': repo_name,
          },
        }
    if method == 'pullrequest:comment_created':
      # https://confluence.atlassian.com/bitbucket/event-payloads-740262817.html#EventPayloads-CommentCreated.1
      pr_id=body['pullrequest']['id']
      commit_hash=body['pullrequest']['source']['commit']['hash']
      pr_source=body['pullrequest']['source']
      pr_dest=body['pullrequest']['destination']
      pr_same_repo=(body['pullrequest']['destination']['repository']['full_name'] == body['pullrequest']['source']['repository']['full_name'])
      comment_id=body['comment']['id']
      #TODO pull comment from API
      # count reviewers and approvers
      reviewers_raw = body['pullrequest']['reviewers'] # TODO maybe needs to be participants
      reviewers=[p['user']['username'] for p in reviewers_raw] #TODO should we downcase?
      approvers=[p['user']['username'] for p in reviewers_raw if p['approved']]
      #TODO count code status
      code_ok=self.commit_code_ok(repo_org,repo_name,commit_hash)
      comment_body=body['comment']['content']['raw']
      ret['event'] = {
          'type': 'pr:comment',
          'pr': {
            'id': pr_id,
            'src_branch': pr_source['branch'],
            'dst_branch': pr_dest['branch'],
            'same_repo': pr_same_repo,
            'reviewers': reviewers,
            'approvers': approvers,
            'code_ok': code_ok,
            },
          'text': comment_body,
          }
    elif method == 'repo:push':
      raw_changes=body['push']['changes']
      raw_changes=filter(lambda c: not c['closed'],raw_changes) # reject deletion notifications
      changes = [ {'branch': c['new']['name'], 'commit': c['new']['target']['hash']} for c in raw_changes ]
      branch=body['push']['changes']
      commit=''
      ret['event']= {
          'type': 'push',
          'changes': changes, # Note: this is an array that can be empty
          }
    else:
      #TODO log ignoring event
      pass

    return ret

    def post_commit_test(self, organization, name, commit, builder_type, url, result):
      self.post_commit_comment(organization, name, commit,"Test by %s: **%s**  \n%s"%(builder_type,('passed' if result else 'failed'),url))
      #XXX only supporting a single builder
      self.set_commit_approval(organization, name, commit, result)

    #TODO rename?
    def post_pr_message(self, organization, name, pr, message):
      self.post_pr_comment(organization,name,pr, message)
