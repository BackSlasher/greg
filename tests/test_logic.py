# testing greg.logic

import unittest
import mock
import greg.logic

import greg.bridge_provider
import greg.bridge_builder

class TestLogic(unittest.TestCase):
    @mock.patch('greg.bridge_provider')
    @mock.patch('greg.bridge_builder')
    def test_test(self,bridge_builder_mock,bridge_provider_mock):
        probri = bridge_provider_mock.locate_bridge_by_url.return_value
        bubri = bridge_builder_mock.locate_bridge.return_value
        bubri.parse_payload.return_value = {
                'source': {
                    'provider': 'mockin',
                    'organization': 'bla',
                    'name': 'blu',
                    'commit': 'bli',
                    },
                'report': True,
                'context': 'test',
                'url': 'glog',
                'good': False,
                }
        greg.logic.build('jenkins','bod','param')
        probri.post_pr_message.assert_not_called()
        probri.post_commit_test.assert_called_once_with('bla', 'blu', 'bli',
                builder_type='jenkins', url='glog', result=False)

    @mock.patch('greg.bridge_provider')
    @mock.patch('greg.bridge_builder')
    def test_provider_failed(self,bridge_builder_mock,bridge_provider_mock):
        probri = bridge_provider_mock.locate_bridge_by_url.return_value
        bubri = bridge_builder_mock.locate_bridge.return_value
        bubri.parse_payload.return_value = {
                'source': {
                    'provider': 'mockin',
                    'organization': 'bla',
                    'name': 'blu',
                    'commit': 'bli',
                    },
                'pr':5,
                'report': True,
                'context': 'merge',
                'url': 'glog',
                'good': False,
                }
        greg.logic.build('jenkins','bod','param')
        probri.post_pr_message.assert_called_once_with('bla', 'blu', 5, 'Merge **failed**  \nglog')
        probri.post_commit_test.assert_not_called()

    @mock.patch('greg.bridge_provider')
    @mock.patch('greg.bridge_builder')
    def test_provider_failed(self,bridge_builder_mock,bridge_provider_mock):
        probri = bridge_provider_mock.locate_bridge_by_url.return_value
        bubri = bridge_builder_mock.locate_bridge.return_value
        bubri.parse_payload.return_value = {
                'source': {
                    'provider': 'mockin',
                    'organization': 'bla',
                    'name': 'blu',
                    'commit': 'bli',
                    },
                'pr':5,
                'report': True,
                'context': 'merge',
                'url': 'glog',
                'good': True,
                }
        greg.logic.build('jenkins','bod','param')
        probri.post_pr_message.assert_not_called()
        probri.post_commit_test.assert_not_called()

    def test_allowed_merge_different_repo(self):
        payload = {'event': {'pr': {
            'same_repo': False,
            'reviewers': ['alfred', 'bonnie'],
            'approvers': ['alfred', 'sansa', 'bonnie'],
            'code_ok': True,
            }}}
        # This should fail on non-identical repos
        res = greg.logic.allowed_merge(payload)
        self.assertEqual(res[0],False)

    def test_allowed_merge_missing_approvers(self):
        payload = {'event': {'pr': {
            'same_repo': True,
            'reviewers': ['alfred', 'bonnie'],
            'approvers': ['alfred', 'sansa'],
            'code_ok': True,
            }}}
        # This should fail on missing approval from bonnie
        res = greg.logic.allowed_merge(payload)
        self.assertEqual(res[0],False)

    def test_allowed_merge_bad_code(self):
        payload = {'event': {'pr': {
            'same_repo': True,
            'reviewers': [],
            'approvers': [],
            'code_ok': False,
            }}}
        # Should fail over bad code
        res = greg.logic.allowed_merge(payload)
        self.assertEqual(res[0],False)

    def test_allowed_merge_bad_code(self):
        payload = {'event': {'pr': {
            'same_repo': True,
            'reviewers': ['alfred', 'bonnie'],
            'approvers': ['alfred', 'sansa', 'bonnie'],
            'code_ok': True,
            }}}
        # Should pass
        res = greg.logic.allowed_merge(payload)
        self.assertEqual(res[0],True)
