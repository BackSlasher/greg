  # testing greg.provider.bitbucket

import os
import unittest
from mock import MagicMock
from greg.provider.bitbucket import BridgeProviderBitbucket

class TestBridgeProviderBitbucket(unittest.TestCase):
  # posting comment for pr
  def test_pr_comment(self):
    testee = BridgeProviderBitbucket({
      'username': 'greg',
      'password': 'grog',
      'incoming_token': 'glig',
      })
    testee.api = MagicMock()
    testee.post_pr_comment('bla','blu','1','hi')
    testee.api.assert_called_once_with('1.0','repositories/bla/blu/pullrequests/1/comments',{'content':'hi'}, 'post')

  # posting comment for commit
  def test_commit_comment(self):
    testee = BridgeProviderBitbucket({
      'username': 'greg',
      'password': 'grog',
      'incoming_token': 'glig',
      })
    testee.api = MagicMock()
    testee.post_commit_comment('bla','blu','1','hello')
    testee.api.assert_called_once_with('1.0','repositories/bla/blu/changesets/1/comments',{'content':'hello'}, 'post')
  # approving commit

  def test_commit_approve(self):
    testee = BridgeProviderBitbucket({
      'username': 'greg',
      'password': 'grog',
      'incoming_token': 'glig',
      })
    testee.api = MagicMock()
    testee.get_commit_approval = MagicMock()
    testee.get_commit_approval.return_value=False
    testee.set_commit_approval('bla','blu','1',True)
    testee.api.assert_called_once_with('2.0','repositories/bla/blu/commit/1/approve',method='post')

  # disapproving commit
  def test_commit_disapprove(self):
    testee = BridgeProviderBitbucket({
      'username': 'greg',
      'password': 'grog',
      'incoming_token': 'glig',
      })
    testee.api = MagicMock()
    testee.get_commit_approval = MagicMock()
    testee.get_commit_approval.return_value=True
    testee.set_commit_approval('bla','blu','1',False)
    testee.api.assert_called_once_with('2.0','repositories/bla/blu/commit/1/approve',method='delete')

  def test_commit_notouch(self):
    testee = BridgeProviderBitbucket({
      'username': 'greg',
      'password': 'grog',
      'incoming_token': 'glig',
      })
    testee.api = MagicMock()
    testee.get_commit_approval = MagicMock()
    testee.get_commit_approval.return_value=True
    testee.set_commit_approval('bla','blu','1',True)
    testee.api.assert_not_called()

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
    headers={
        'X-Event-Key': 'repo:push',
        }
    querystring={
        'token': 'glig',
        }
    body_path = os.path.join(os.path.dirname(__file__), 'responses/bitbucket_code_push.txt')
    with open (body_path) as myfile:
        body=myfile.read()

    res = testee.parse_payload(body,headers,querystring)
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
    headers={
        'X-Event-Key': 'pullrequest:comment_created',
        }
    querystring={
        'token': 'glig',
        }
    body_path = os.path.join(os.path.dirname(__file__), 'responses/bitbucket_pr_comment.txt')
    with open (body_path) as myfile:
        body=myfile.read()

    testee.get_commit_approval = MagicMock(return_value=True)
    res = testee.parse_payload(body,headers,querystring)
    self.assertEqual(res['repo']['provider'],'bitbucket')
    self.assertEqual(res['repo']['organization'],'dy-devops')
    self.assertEqual(res['repo']['name'],'janitor-starter')
    self.assertEqual(res['event']['type'],'pr:comment')
    self.assertEqual(res['event']['pr']['src_branch'],'add-webshot')
    self.assertEqual(res['event']['pr']['dst_branch'],'master')
    self.assertEqual(res['event']['pr']['same_repo'],True)
    self.assertEqual(res['event']['pr']['reviewers'],set())
    self.assertEqual(res['event']['pr']['approvers'],set())
    self.assertEqual(res['event']['pr']['id'],1)
    self.assertEqual(res['event']['pr']['code_ok'],True)

  def test_url_base_compare(self):
    testee = BridgeProviderBitbucket({
      'username': 'greg',
      'password': 'grog',
      'incoming_token': 'glig',
      })
    self.assertEqual(testee.url_base_compare(
        'http://bla.com/bla',
        'http://bla.com/'
        ),True)
    self.assertEqual(testee.url_base_compare(
        'http://bla.com/bla',
        'http://bla.org/bla'
        ),False)

