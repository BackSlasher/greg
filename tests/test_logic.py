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

    @mock.patch('greg.config')
    @mock.patch('greg.bridge_provider')
    def test_merge_no_job(self, greg_bridge_provider_mock, greg_config_mock):
        import collections
        probri = greg_bridge_provider_mock.locate_bridge.return_value
        probri.parse_payload.return_value = {
                'repo': {
                    'provider': 'shake',
                    'organization': 'it',
                    'name': 'off',
                    },
                'event': {
                    'type': 'pr:comment',
                    'text': 'greg please',
                    },
                }
        config = greg_config_mock.get_config.return_value
        config.get_job.return_value = None
        ret_type = collections.namedtuple('merge_review', ['allowed','issues'])
        old_allowed_merge = greg.logic.allowed_merge
        greg.logic.allowed_merge = lambda x: ret_type(True,[])
        greg.logic.repo('bb','',{})
        greg.logic.allowed_merge = old_allowed_merge
        probri.post_pr_message.assert_called_once_with('it','off','No merge job found. Merge manually?')

    @mock.patch('greg.bridge_provider')
    def test_merge_not_allowed(self, greg_bridge_provider_mock):
        import collections
        probri = greg_bridge_provider_mock.locate_bridge.return_value
        probri.parse_payload.return_value = {
                'repo': {
                    'provider': 'shake',
                    'organization': 'it',
                    'name': 'off',
                    },
                'event': {
                    'type': 'pr:comment',
                    'text': 'greg please',
                    },
                }
        ret_type = collections.namedtuple('merge_review', ['allowed','issues'])
        old_allowed_merge = greg.logic.allowed_merge
        greg.logic.allowed_merge = lambda x: ret_type(False,[])
        greg.logic.repo('bb','',{})
        greg.logic.allowed_merge = old_allowed_merge
        probri.post_pr_message.assert_called_once_with('it','off','**Will not merge**  \n')

    @mock.patch('greg.config')
    @mock.patch('greg.bridge_provider')
    @mock.patch('greg.bridge_builder')
    def test_merge_allow(self, greg_bridge_builder_mock, greg_bridge_provider_mock, greg_config_mock):
        import collections
        probri = greg_bridge_provider_mock.locate_bridge.return_value
        probri.parse_payload.return_value = {
                'repo': {
                    'provider': 'shake',
                    'organization': 'it',
                    'name': 'off',
                    },
                'event': {
                    'type': 'pr:comment',
                    'text': 'greg please',
                    'pr': {
                        'src_branch': 'donald',
                        'dst_branch': 'duck',
                        'id': 1,
                        },
                    },
                }
        config = greg_config_mock.get_config.return_value
        config.get_job.return_value = collections.namedtuple('Job',['name','builder'])('yugi','oh')
        ret_type = collections.namedtuple('merge_review', ['allowed','issues'])
        old_allowed_merge = greg.logic.allowed_merge
        greg.logic.allowed_merge = lambda x: ret_type(True,[])
        greg.logic.repo('bb','',{})
        greg.logic.allowed_merge = old_allowed_merge
        probri.post_pr_message.assert_not_called()
        greg_bridge_builder_mock.locate_bridge.return_value.start_build.assert_called_once_with('yugi', {
            'PROVIDER': 'shake',
            'USER': 'it',
            'REPO': 'off',
            'COMMIT': 'donald',
            'TARGET_BRANCH': 'duck',
            'PR': 1,
            'REPORT': True,
            })

    @mock.patch('greg.bridge_provider')
    def test_ok_notok(self, greg_bridge_provider_mock):
        import collections
        probri = greg_bridge_provider_mock.locate_bridge.return_value
        probri.parse_payload.return_value = {
                'repo': {
                    'provider': 'shake',
                    'organization': 'it',
                    'name': 'off',
                    },
                'event': {
                    'type': 'pr:comment',
                    'text': 'greg ok',
                    'pr': {
                        'src_branch': 'donald',
                        'dst_branch': 'duck',
                        'id': 1,
                        },
                    },
                }
        ret_type = collections.namedtuple('merge_review', ['allowed','issues'])
        old_allowed_merge = greg.logic.allowed_merge
        greg.logic.allowed_merge = lambda x: ret_type(False,[])
        greg.logic.repo('bb','',{})
        greg.logic.allowed_merge = old_allowed_merge
        probri.post_pr_message.assert_called_with('it','off','**Not ready to merge**  \n')

    @mock.patch('greg.bridge_provider')
    def test_ok_reallyok(self, greg_bridge_provider_mock):
        import collections
        probri = greg_bridge_provider_mock.locate_bridge.return_value
        probri.parse_payload.return_value = {
                'repo': {
                    'provider': 'shake',
                    'organization': 'it',
                    'name': 'off',
                    },
                'event': {
                    'type': 'pr:comment',
                    'text': 'greg ok',
                    'pr': {
                        'src_branch': 'donald',
                        'dst_branch': 'duck',
                        'id': 1,
                        },
                    },
                }
        ret_type = collections.namedtuple('merge_review', ['allowed','issues'])
        old_allowed_merge = greg.logic.allowed_merge
        greg.logic.allowed_merge = lambda x: ret_type(True,[])
        greg.logic.repo('bb','',{})
        greg.logic.allowed_merge = old_allowed_merge
        probri.post_pr_message.assert_called_with('it','off','**Ready to merge**')

    @mock.patch('greg.config')
    @mock.patch('greg.bridge_provider')
    @mock.patch('greg.bridge_builder')
    def test_test_nojob(self, greg_bridge_builder_mock, greg_bridge_provider_mock, greg_config_mock):
        import collections
        probri = greg_bridge_provider_mock.locate_bridge.return_value
        probri.parse_payload.return_value = {
                'repo': {
                    'provider': 'shake',
                    'organization': 'it',
                    'name': 'off',
                    },
                'event': {
                    'type': 'push',
                    'changes': [
                        {'commit':'b33f'},
                        ],
                }
            }
        config = greg_config_mock.get_config.return_value
        config.get_job.return_value = collections.namedtuple('Job',['name','builder'])('yugi','oh')
        ret_type = collections.namedtuple('merge_review', ['allowed','issues'])
        old_allowed_merge = greg.logic.allowed_merge
        greg.logic.allowed_merge = lambda x: ret_type(True,[])
        greg.logic.repo('bb','',{})
        greg.logic.allowed_merge = old_allowed_merge
        probri.post_pr_message.assert_not_called()
        greg_bridge_builder_mock.locate_bridge.return_value.start_build.assert_called_once_with('yugi', {
            'PROVIDER': 'shake',
            'USER': 'it',
            'REPO': 'off',
            'COMMIT': 'b33f',
            'REPORT': True,
            })
