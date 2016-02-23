# testing greg.provider.github

import unittest
from mock import MagicMock
from greg.provider.github import BridgeProviderGithub

class TestBridgeProviderGithub(unittest.TestCase):
    # posting comment for pr
    def test_pr_message(self):
        testee = BridgeProviderGithub({
            'username': 'greg',
            'password': 'grog',
            'incoming_token': 'glig',
            })
        testee.api = MagicMock()
        testee.post_pr_message('bla','blu',1,'hi')
        testee.api.assert_called_once_with('/repos/bla/blu/issues/1/comments',form_data = {'body': 'hi'}, request_type='json')

    # posting good code status

    # posting bad code status

    # trigger commit test

    # parsing payload - code push

    # parsing payload - PR comment

    # webhook maintenance
