
from greg.provider import BridgeProvider
import requests
import json

class BridgeProviderGithub(BridgeProvider):

  def __init__(self, dic):
    self.username=dic['username']
    self.password=dic['password']
    self.incoming_token=dic['incoming_token']
    self._my_username=None

  def api_raw(self,url,form_data={},method=None,request_type=None):
    headers={}
    headers['Accept']='application/vnd.github.v3+json'
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
      raise Exception("Bad request_type %s"%(request_type))
    resp=requests.request(method=method, url=url, data=data, headers=headers, auth=(self.username, self.password))
    resp.raise_for_status() # raise error if there's an issue
    body = resp.text
    if resp.headers['content-type'].startswith('application/json'):
      body = json.loads(body)
      # Handle pagination
      if method == 'GET' and type(body)==dict and body.keys() and set(body.keys()).issubset(set(['size','page','pagelen','next','previous','values'])):
        values = body['values']
        if body.has_key('next'):
          values.extend(self.api_raw(body['next']))
        return values
    return body

  def api(self,path,form_data={},method=None,request_type=None):
    uri = 'https://api.github.com/%s' % (path)
    return self.api_raw(uri, form_data, method, request_type)

  def my_username(self):
      if not self._my_username:
        self._my_username=self.api('1.0','user')['login']
      return self._my_username


  def comment_is_referencing_me(self, comment_text):
    import re
    return re.match('\\b@%s\\b' % (re.escape(self.my_username())), comment_text)

  def comments_collect_reviewers(self,comment_object_list):
    import re
    reviewers=set()
    for comment_object in comment_object_list:
      text = comment_object['body']
      if not self.comment_is_referencing_me(text): continue # Skip if not referncing me
      mentions = set(re.findall(r'(?<!\w)@(\w)+',text))
      reviewers.update(mentions)
    reviewers.discard(self.my_username())
    return reviewers

  def comments_collect_approvers(self,comment_object_list):
    import re
    approvers=set()
    for comment_object in comment_object_list:
      text = comment_object['body']
      writer = comment_object['user']['login']
      if not self.comment_is_referencing_me(text): continue # Skip if not referncing me
      # Find approving comments
      has_lgtm = re.match(r'\bLGTM\b', text, re.IGNORECASE) is not None
      # Find rejecting comments
      has_not_lgtm = re.match(r'\bnot LGTM\b', text, re.IGNORECASE) is not None
      if has_not_lgtm:
        approvers.remove(writer)
      elif has_lgtm:
        approvers.add(writer)
      pass
    approvers.discard(self.my_username())
    return approvers

  def parse_payload(self, body, headers={}, querystring={}):
    body = json.loads(body)
    ret={
            'repo': {
                'provider': 'github',
                'organization': body['repository']['owner']['login'],
                'name': body['repository']['name'],
                },
            'event': {},
    }
    event_type = headers['X-GitHub-Event']
    # make sure pull_request
    if event_type == 'IssueCommentEvent':
        # make sure is pull request
        if not body['issue'].has_key('pull_request'): pass
        pr_object = self.api_raw(body['issue']['pull_request']['url'])
        comments_object = self.api_raw(pr_object['comments_url'])


        ret['event']['type']='pr:comment'
        pr_hash = {}
        pr_hash['id']=body['number']
        pr_hash['src_branch']=pr_object['head']['ref']
        pr_hash['dst_branch']=pr_object['base']['ref']
        pr_hash['same_repo']= (pr_object['base']['repo']['full_name'] == pr_object['head']['repo']['full_name'])

        # Build reviewers and approvers from comments
        # Reviewers: all users that are tagged, in any message where I am tagged, with the word "review" (should match reviewers and reviewed)
        # @greg @backslasher should review
        # Approvers: Users that made a comment that has some constructive text

        ret['event']['pr']=pr_hash


    return ret

  def post_commit_test(self, organization, name, commit, builder_type, url, result):
    # /repos/:owner/:repo/statuses/:sha
    '''
    {
      "state": "success",
      "target_url": "https://example.com/build/status",
      "description": "The build succeeded!",
      "context": "continuous-integration/jenkins"
    }
    '''
    state_string=''
    #TODO handle None as "pending"
    if result:
        state_string='success'
    else:
        state_string='error'
    description_string = '%s: %s' % (builder_type, state_string)
    return self.api('/repos/%s/%s/statuses/%s' % (organization,name,commit), form_data = {
        'state': state_string,
        'target_url': url,
        'description': state_string, # TODO something prettier?
        'context': builder_type,
        }, request_type='json')

  def post_pr_message(self, organization, name, pr, message):
    # POST /repos/:owner/:repo/issues/:number/comments
    # https://developer.github.com/v3/issues/comments/
    # body: { "body": "Me too"}
    return self.api('/repos/%s/%s/issues/%d/comments' % (organization,name,pr), form_data = {'body': message}, request_type='json')
