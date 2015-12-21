# testing greg.config

import unittest
import mock
import greg.config

class TestConfig(unittest.TestCase):
    # Test:
    # Parsing job
    def test_parse_job(self):
        j = greg.config.JobConfig({'name': 'a', 'builder': 'b'})
        self.assertEqual(j.name, 'a')
        self.assertEqual(j.builder, 'b')

    # Failing to parse a bad job
    def test_parse_job_fail(self):
        with self.assertRaises(Exception):
            j = greg.config.JobConfig({})


    # Parse repo config
    def test_parse_repo(self):
        import re
        r = greg.config.RepoConfig('bobert',['arya','ned'],['iron','/man/'],{
            'test': {'name': 'knownothing', 'builder': 'jonsnow'},
            'merge': {'name': 'winter', 'builder': 'iscoming'},
            })
        self.assertEqual(r.provider,'bobert')
        self.assertEqual(r.organizations,['arya','ned'])
        self.assertEqual(r.names,set(['iron']))
        self.assertEqual(r.names_regexps,set([re.compile('man')]))
        self.assertEqual(r.jobs['test'].name,'knownothing')
        self.assertEqual(r.jobs['test'].builder,'jonsnow')
        self.assertEqual(r.jobs['merge'].name,'winter')
        self.assertEqual(r.jobs['merge'].builder,'iscoming')

        # Check matches
        self.assertEqual(r.match('bobert','arya','man'),True)
        self.assertEqual(r.match('bobert','arya','iron'),True)
        self.assertEqual(r.match('bobert','arya','snow'),False)
