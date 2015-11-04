  # testing greg.bridge_provider.bitbucket

import os
import unittest

class TestBridgeProviderBitbucket(unittest.TestCase):
  # test list:
  # posting comment for pr
  # posting comment for commit
  # approving commit
  # disapproving commit
  # reporting a test result
  # parsing a payload - PR comment
  # parsing a payload - code push
  def test_payload_code(self):
    from mock import MagicMock
    from greg.bridge_provider.bitbucket import BridgeProviderBitbucket
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

