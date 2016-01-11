# testing greg.logic

import unittest
import mock
import greg.logic

import greg.provider
import greg.builder

class TestLogic(unittest.TestCase):
    @mock.patch('greg.provider')
    @mock.patch('greg.builder')
    def test_test(self,builder_mock,provider_mock):
        probri = provider_mock.locate_bridge_by_url.return_value
        bubri = builder_mock.locate_bridge.return_value
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

    @mock.patch('greg.provider')
    @mock.patch('greg.builder')
    def test_provider_failed(self,builder_mock,provider_mock):
        probri = provider_mock.locate_bridge_by_url.return_value
        bubri = builder_mock.locate_bridge.return_value
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

    @mock.patch('greg.provider')
    @mock.patch('greg.builder')
    def test_provider_failed(self,builder_mock,provider_mock):
        probri = provider_mock.locate_bridge_by_url.return_value
        bubri = builder_mock.locate_bridge.return_value
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
    @mock.patch('greg.provider')
    def test_merge_no_job(self, greg_provider_mock, greg_config_mock):
        import collections
        probri = greg_provider_mock.locate_bridge.return_value
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
        config.get_job.return_value = None
        ret_type = collections.namedtuple('merge_review', ['allowed','issues'])
        old_allowed_merge = greg.logic.allowed_merge
        greg.logic.allowed_merge = lambda x: ret_type(True,[])
        greg.logic.repo('bb','',{})
        greg.logic.allowed_merge = old_allowed_merge
        probri.post_pr_message.assert_called_once_with('it','off',1, message='No merge job found. Merge manually?')

    @mock.patch('greg.provider')
    def test_merge_not_allowed(self, greg_provider_mock):
        import collections
        probri = greg_provider_mock.locate_bridge.return_value
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
        ret_type = collections.namedtuple('merge_review', ['allowed','issues'])
        old_allowed_merge = greg.logic.allowed_merge
        greg.logic.allowed_merge = lambda x: ret_type(False,[])
        greg.logic.repo('bb','',{})
        greg.logic.allowed_merge = old_allowed_merge
        probri.post_pr_message.assert_called_once_with('it','off',1, message='**Will not merge**  \n')

    @mock.patch('greg.config')
    @mock.patch('greg.provider')
    @mock.patch('greg.builder')
    def test_merge_allow(self, greg_builder_mock, greg_provider_mock, greg_config_mock):
        import collections
        probri = greg_provider_mock.locate_bridge.return_value
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
        greg_builder_mock.locate_bridge.return_value.start_build.assert_called_once_with(
            {
              'organization': 'it',
              'name': 'off',
              'provider': 'shake'
            },
            'yugi',
            {
              'PR': 1,
              'COMMIT': 'donald',
              'REPORT': True,
              'TARGET_BRANCH': 'duck'
            })

    @mock.patch('greg.provider')
    def test_ok_notok(self, greg_provider_mock):
        import collections
        probri = greg_provider_mock.locate_bridge.return_value
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
        probri.post_pr_message.assert_called_with('it','off',1, message='**Not ready to merge**  \n')

    @mock.patch('greg.provider')
    def test_ok_reallyok(self, greg_provider_mock):
        import collections
        probri = greg_provider_mock.locate_bridge.return_value
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
        probri.post_pr_message.assert_called_with('it','off',1, message='**Ready to merge**')

    @mock.patch('greg.config')
    @mock.patch('greg.provider')
    @mock.patch('greg.builder')
    def test_test_nojob(self, greg_builder_mock, greg_provider_mock, greg_config_mock):
        import collections
        probri = greg_provider_mock.locate_bridge.return_value
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
        greg_builder_mock.locate_bridge.return_value.start_build.assert_called_once_with(
                {'organization': 'it', 'name': 'off', 'provider': 'shake'},
                'yugi',
                {'REPORT': True, 'COMMIT': 'b33f'})
