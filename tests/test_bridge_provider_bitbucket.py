  # testing greg.bridge_provider.bitbucket

import os
import unittest
from mock import MagicMock
from greg.bridge_provider.bitbucket import BridgeProviderBitbucket

class TestBridgeProviderBitbucket(unittest.TestCase):
  # test list:
  # posting comment for pr
  # posting comment for commit
  # approving commit
  # disapproving commit
  # reporting a test result
  def test_commit_test(self):
    testee = BridgeProviderBitbucket({
      'username': 'greg',
      'password': 'grog',
      'incoming_token': 'glig',
      })
    testee.set_commit_approval = MagicMock()
    testee.post_commit_comment = MagicMock()
    testee.post_commit_test('bla','blu','1','j','http://google.com',True)
    testee.post_commit_comment.assert_called_once_with('bla','blu','1','Test by j: **passed**  \nhttp://google.com')
    testee.set_commit_approval.assert_called_once_with('bla','blu','1',True)


  # parsing a payload - code push
  def test_payload_push(self):
    testee = BridgeProviderBitbucket({
      'username': 'greg',
      'password': 'grog',
      'incoming_token': 'glig',
      })
    params ={
        'X-Event-Key': 'repo:push',
        'token': 'glig',
        }
    body_path = os.path.join(os.path.dirname(__file__), 'responses/bitbucket_code_push.txt')
    with open (body_path) as myfile:
        body=myfile.read()

    res = testee.parse_payload(body,params)
    self.assertEqual(res['repo']['provider'],'bitbucket')
    self.assertEqual(res['repo']['organization'],'dy-devops')
    self.assertEqual(res['repo']['name'],'janitor-starter')
    self.assertEqual(res['event']['type'],'push')
    self.assertEqual(len(res['event']['changes']),1)
    self.assertEqual(res['event']['changes'][0]['commit'],'bf89e3d025b08c78009fc2c6884916add07314e1')
    self.assertEqual(res['event']['changes'][0]['branch'],'bla')

  # parsing a payload - PR comment
  def test_payload_comment(self):
    testee = BridgeProviderBitbucket({
      'username': 'greg',
      'password': 'grog',
      'incoming_token': 'glig',
      })
    params ={
        'X-Event-Key': 'pullrequest:comment_created',
        'token': 'glig',
        }
    body_path = os.path.join(os.path.dirname(__file__), 'responses/bitbucket_pr_comment.txt')
    with open (body_path) as myfile:
        body=myfile.read()

    testee.commit_code_ok = MagicMock(return_value=True)
    res = testee.parse_payload(body,params)
    self.assertEqual(res['repo']['provider'],'bitbucket')
    self.assertEqual(res['repo']['organization'],'dy-devops')
    self.assertEqual(res['repo']['name'],'janitor-starter')
    self.assertEqual(res['event']['type'],'pr:comment')
    self.assertEqual(res['event']['pr']['src_branch'],'add-webshot')
    self.assertEqual(res['event']['pr']['dst_branch'],'master')
    self.assertEqual(res['event']['pr']['same_repo'],True)
    self.assertEqual(res['event']['pr']['reviewers'],[])
    self.assertEqual(res['event']['pr']['approvers'],[])
    self.assertEqual(res['event']['pr']['id'],1)
    self.assertEqual(res['event']['pr']['code_ok'],True)

