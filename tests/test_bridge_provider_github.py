# testing greg.provider.github

import unittest
from mock import MagicMock
from greg.provider.github import BridgeProviderGithub
import os

class TestBridgeProviderGithub(unittest.TestCase):

    # Helper for testing
    def get_testee(self):
        testee = BridgeProviderGithub({
            'username': 'greg',
            'password': 'grog',
            'incoming_token': 'glig',
            })
        return testee


    # posting comment for pr
    def test_pr_message(self):
        testee = self.get_testee()
        testee.api = MagicMock()
        testee.post_pr_message('bla','blu',1,'hi')
        testee.api.assert_called_once_with('/repos/bla/blu/issues/1/comments',form_data = {'body': 'hi'}, request_type='json')

    # posting good code status
    def test_commit_test_good(self):
        testee = self.get_testee()
        testee.api = MagicMock()
        testee.post_commit_test('org','nom','com','jen','goog',True)
        testee.api.assert_called_once_with('/repos/org/nom/statuses/com',
                form_data = {
                    'state': 'success',
                    'target_url': 'goog',
                    'description': 'success',
                    'context': 'jen'
                },
                request_type='json')

    # posting bad code status
    def test_commit_test_bad(self):
        testee = self.get_testee()
        testee.api = MagicMock()
        testee.post_commit_test('org','nom','com','jen','goog',False)
        testee.api.assert_called_once_with('/repos/org/nom/statuses/com',
                form_data = {
                    'state': 'error',
                    'target_url': 'goog',
                    'description': 'error',
                    'context': 'jen'
                },
                request_type='json')

    # parsing payload - code push

    # parsing payload - PR comment
    def test_payload_comment(self):
        testee = self.get_testee()
        headers = {
                'X-GitHub-Event': 'IssueCommentEvent',
                }
        querystring={
                'token': 'glig',
                }
        body_path = os.path.join(os.path.dirname(__file__), 'responses/github_pr_comment.txt')
        with open (body_path) as myfile:
            body=myfile.read()

        res = testee.parse_payload(body,headers,querystring)
        print res
        self.assertEqual(res['repo']['provider'], 'github')
        self.assertEqual(res['repo']['organization'],'dy-devops')
        self.assertEqual(res['repo']['name'],'janitor-starter')
        self.assertEqual(res['event']['type'],'pr:comment')
        self.assertEqual(res['event']['pr']['src_branch'],'add-webshot')
        self.assertEqual(res['event']['pr']['dst_branch'],'master')
        self.assertEqual(res['event']['pr']['same_repo'],True)
        self.assertEqual(res['event']['pr']['reviewers'],set(['BackSlasher']))
        self.assertEqual(res['event']['pr']['approvers'],set(['BackSlasher']))
        self.assertEqual(res['event']['pr']['id'],1)
        self.assertEqual(res['event']['pr']['code_ok'],True)

    # webhook maintenance
