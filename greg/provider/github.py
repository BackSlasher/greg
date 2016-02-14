
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

  def post_pr_message(self, organization, name, pr, message):
    # POST /repos/:owner/:repo/issues/:number/comments
    # https://developer.github.com/v3/issues/comments/
    # body: { "body": "Me too"}
    pass
