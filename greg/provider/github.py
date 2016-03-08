
from greg.provider import BridgeProvider
import requests
import json
import re

class BridgeProviderGithub(BridgeProvider):

  def __init__(self, dic):
    self.username=dic['username']
    self.password=dic['password']
    self.incoming_token=dic['incoming_token']
    self._my_username=None

  def api_next_page(self, link_header):
    raw_links = link_header.split(',')
    raw_next_link = [l for l in raw_links if ('rel="next"' in l)][0]
    link = re.match('<(.+)>',raw_next_link).groups()[0]
    return link

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
      links = resp.headers.get('Link')
      if method == 'GET' and type(body)==list and links and ('rel="next"' in links):
        next_page_link = self.api_next_page(links)
        new_body = self.api_raw(next_page_link,form_data=form_data, method=method, request_type=request_type)
        body.extend(new_body)
    return body

  def api(self,path,form_data={},method=None,request_type=None):
    uri = 'https://api.github.com/%s' % (path)
    return self.api_raw(uri, form_data, method, request_type)

  def my_username(self):
      if not self._my_username:
        self._my_username=self.api('user')['login']
      return self._my_username


  def comment_is_referencing_me(self, comment_text):
    return re.search(r'(?<!\w)@%s\b' % (re.escape(self.my_username())), comment_text)

  def comments_collect_reviewers(self,comment_object_list):
    import re
    reviewers=set()
    for comment_object in comment_object_list:
      text = comment_object['body']
      if not self.comment_is_referencing_me(text): continue # Skip if not referncing me
      # http://stackoverflow.com/questions/30281026/regex-parsing-github-usernames-javascript
      mentions = set(re.findall(r'\B@([a-z0-9](?:-?[a-z0-9]){0,38})',text))
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
      has_lgtm = re.search(r'\bLGTM\b', text, re.IGNORECASE) is not None
      # Find rejecting comments
      has_not_lgtm = re.search(r'\bnot LGTM\b', text, re.IGNORECASE) is not None
      if has_not_lgtm:
        approvers.remove(writer)
      elif has_lgtm:
        approvers.add(writer)
      pass
    approvers.discard(self.my_username())
    return approvers

  def get_code_status(self, org, repo_name, commit):
    target_url = 'repos/%s/%s/status/%s' % (org, repo_name, commit)
    resp = self.api(target_url)
    state_string = resp['state']
    return state_string

  def parse_payload(self, body, headers={}, querystring={}):
    import re
    event_type = headers['X-Github-Event']

    presented_token=querystring['token']
    # Verify token
    if self.incoming_token != presented_token: raise Exception('Bad token')

    # Return nothing if ping, to ignore this event
    if event_type == 'ping':
        return

    body = json.loads(body)
    repo_name = body['repository']['name']
    ret={
            'repo': {
                'provider': 'github',
                # organization provided below, differs between events
                'name': repo_name,
                },
            'event': {},
    }
    # IssueCommentEvent
    if event_type == 'issue_comment':
        ret['repo']['organization'] = body['repository']['owner']['login']
        # make sure is pull request
        if not body['issue'].has_key('pull_request'): return
        pr_object = self.api_raw(body['issue']['pull_request']['url'])
        comments_object = self.api_raw(pr_object['comments_url'])

        ret['event']['type']='pr:comment'
        pr_hash = {}
        pr_hash['id']=pr_object['number']
        pr_hash['src_branch']=pr_object['head']['ref']
        pr_hash['dst_branch']=pr_object['base']['ref']
        pr_hash['same_repo']= (pr_object['base']['repo']['full_name'] == pr_object['head']['repo']['full_name'])

        # Build reviewers and approvers from comments
        # Approvers: Users that made a comment that has some constructive text
        pr_hash['reviewers']=self.comments_collect_reviewers(comments_object)
        pr_hash['approvers']=self.comments_collect_approvers(comments_object)

        # Check if code ok
        # TODO make a more detailed message about which checks failed?
        pr_hash['code_ok'] = self.get_code_status(ret['repo']['organization'], repo_name, pr_object['head']['sha'])

        ret['event']['pr']=pr_hash

        # Collect text
        ret['event']['text']=body['comment']['body']
    # PushEvent
    elif event_type == 'push':
      ret['repo']['organization'] = body['repository']['owner']['name']
      ret['event']= {
          'type': 'push',
          'changes': [
              {
                'branch': body['base_ref'],
                'commit': body['after'],
              }
            ],
      }
    else:
      raise Exception('Unknown event type '+event_type)

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
    return self.api('repos/%s/%s/statuses/%s' % (organization,name,commit), form_data = {
        'state': state_string,
        'target_url': url,
        'description': builder_type, # TODO something prettier?
        'context': builder_type,
        }, request_type='json')

  def post_pr_message(self, organization, name, pr, message):
    # POST /repos/:owner/:repo/issues/:number/comments
    # https://developer.github.com/v3/issues/comments/
    # body: { "body": "Me too"}
    return self.api('repos/%s/%s/issues/%d/comments' % (organization,name,int(pr)), form_data = {'body': message}, request_type='json')

  # Make sure a repo has a greg webhook
  def ensure_webhook(self,organization,name,my_url):
      proper_hook = {
              'name': 'web',
              'config': {
                  'url': my_url,
                  'content_type': 'json',
                  # TODO add secret
                  },
              'events': ['push', 'issue_comment'],
              'active': True,
              }
      hooks = self.api('repos/%s/%s/hooks'%(organization,name))
      existing_hooks = [hook for hook in hooks if self.url_base_compare(hook['config']['url'],my_url)]
      if len(existing_hooks) == 1:
          # Replace hook if needed
          existing_hook = existing_hooks[0]
          existing_values = [existing_hook[k] for k in proper_hook.keys()]
          existing_ok = existing_values == proper_hook.values()
          if not existing_ok:
              # replace
              self.api(
                      'repos/%s/%s/hooks/%d'%(organization,name,existing_hook['id']),
                      form_data=proper_hook,
                      method='PATCH',
                      request_type='json'
                      )
      else:
          # Delete all hooks if there are any
          for hook in existing_hooks:
              self.api(
                      'repos/%s/%s/hooks/%d'%(organization,name,hook['id']),
                      method='DELETE'
                      )
          # Create new hook
          self.api(
                  'repos/%s/%s/hooks'%(organization,name),
                  form_data=proper_hook,
                  method='POST',
                  request_type='json'
                  )
  # Get all repos in a specific organization
  def list_repos(self,organization):
      return [repo['name'] for repo in self.api('orgs/%s/repos'%(organization))]
