# testing greg.bridge_builder.jenkins

import unittest

class TestBridgeBuilderJenkins(unittest.TestCase):
  # Test list:
  # parse_repo parses git@bla urls
  def test_parse_repo(self):
    from greg.bridge_builder.jenkins import BridgeBuilderJenkins
    testee = BridgeBuilderJenkins({
        'url':'http://wow.com',
        'username': 'greg',
        'password': 'grog',
        'incoming_token': 'hi',
        })
    res=testee.parse_repo('git@bla.com:blu/bli.git')
    self.assertEqual(res[0],'bla.com')
    self.assertEqual(res[1],'blu')
    self.assertEqual(res[2],'bli')
  # parse_payload works with exmaple data
