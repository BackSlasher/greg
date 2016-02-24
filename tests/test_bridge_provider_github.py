# testing greg.provider.github

import unittest
from mock import MagicMock
from greg.provider.github import BridgeProviderGithub
import os
import json

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

    def test_collect_reviewers(self):
        comments = [
                {
                    'body': '@greg review @bla @blu'
                },
                {
                    'body': '@greg hello @bli'
                },
                {
                    'body': 'review @bli'
                }
            ]
        testee = self.get_testee()
        testee.my_username = lambda: 'greg'
        res = testee.comments_collect_reviewers(comments)
        self.assertEqual(res, set(['bla','blu','bli']))

    def test_collect_approvers(self):
        comments = [
                {
                    'user': {'login': 'bla'},
                    'body': '@greg LGTM',
                },
                {
                    'user': {'login': 'bla'},
                    'body': '@greg not LGTM',
                },
                {
                    'user': {'login': 'bli'},
                    'body': 'LGTM',
                },
                {
                    'user': {'login': 'blu'},
                    'body': 'LGTM @greg',
                },
                {
                    'user': {'login': 'blu'},
                    'body': 'not LGTM',
                },
                {
                    'user': {'login': 'bll'},
                    'body': '@greg LGTM',
                },
            ]
        testee = self.get_testee()
        testee.my_username = lambda: 'greg'
        res = testee.comments_collect_approvers(comments)
        self.assertEqual(res, set(['blu','bll']))

    # parsing payload - code push
    def test_payload_push(self):
        testee = self.get_testee()
        headers = {
                'X-GitHub-Event': 'PushEvent',
                }
        querystring={
                'token': 'glig',
                }
        body_path = os.path.join(os.path.dirname(__file__), 'responses/github_push_trigger.txt')
        with open (body_path) as myfile:
            body=myfile.read()
        res = testee.parse_payload(body,headers,querystring)
        print 'nitznitnzintizntiz', res
        self.assertEqual(res['repo']['provider'], 'github')
        self.assertEqual(res['repo']['organization'], 'baxterthehacker')
        self.assertEqual(res['repo']['name'], 'public-repo')
        self.assertEqual(res['event']['type'], 'push')
        self.assertEqual(len(res['event']['changes']), 1)
        self.assertEqual(res['event']['changes'][0]['commit'], '0d1a26e67d8f5eaf1f6ba5c57fc3c7d91ac0fd1c')
        self.assertEqual(res['event']['changes'][0]['branch'], None)


    # parsing payload - PR comment
    def test_payload_comment(self):
        testee = self.get_testee()
        headers = {
                'X-GitHub-Event': 'IssueCommentEvent',
                }
        querystring={
                'token': 'glig',
                }
        body_path = os.path.join(os.path.dirname(__file__), 'responses/github_pr_comment_trigger.txt')
        with open (body_path) as myfile:
            body=myfile.read()

        # TODO patch api_raw:
        # pr, comments, status
        def my_api_raw(url, form_data={}, method=None, request_type=None):
            if '/pulls/' in url:
                url_basic_path = 'github_pr_raw.txt'
            elif '/comments' in url:
                url_basic_path = 'github_pr_comments.txt'

                # https://api.github.com/repos/baxterthehacker/public-repo/statuses/{sha}
            else:
                raise Exception('dunno dis '+url)
            url_path = os.path.join(os.path.dirname(__file__), 'responses',url_basic_path)
            with open (url_path) as myfile:
                url_body=myfile.read()
            ret = json.loads(url_body)
            return ret

        testee.api_raw = my_api_raw
        testee.my_username = lambda: 'greg'
        testee.get_code_status = lambda x,y,z: True

        res = testee.parse_payload(body,headers,querystring)
        self.assertEqual(res['repo']['provider'], 'github')
        self.assertEqual(res['repo']['organization'],'baxterthehacker')
        self.assertEqual(res['repo']['name'],'public-repo')
        self.assertEqual(res['event']['type'],'pr:comment')
        self.assertEqual(res['event']['pr']['src_branch'],'new-topic')
        self.assertEqual(res['event']['pr']['dst_branch'],'master')
        self.assertEqual(res['event']['pr']['same_repo'],True)
        self.assertEqual(res['event']['pr']['reviewers'],set(['octocat', 'bob']))
        self.assertEqual(res['event']['pr']['approvers'],set(['octocat']))
        self.assertEqual(res['event']['pr']['id'],1347)
        self.assertEqual(res['event']['pr']['code_ok'],True)

    # webhook maintenance
