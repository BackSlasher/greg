# testing greg.bridge_builder.jenkins

import unittest

class TestBridgeBuilderJenkins(unittest.TestCase):
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
  def test_parse_payload(self):
    from greg.bridge_builder.jenkins import BridgeBuilderJenkins
    testee = BridgeBuilderJenkins({
        'url':'http://wow.com',
        'username': 'greg',
        'password': 'grog',
        'incoming_token': 'hi',
        })
    querystring = {
            'token': 'hi',
            }

    body ='{"name":"cookbook-test","url":"job/cookbook-test/","build":{"full_url":"http://build1.use.dynamicyield.com:8080/job/cookbook-test/3885/","number":3885,"phase":"COMPLETED","status":"UNSTABLE","url":"job/cookbook-test/3885/","scm":{"url":"git@bitbucket.org:dy-devops/chef-dy-spark.git","branch":"origin/master","commit":"5fd7ed5ea61ff8dab124d17c1c7dd23917f26ed3"},"parameters":{"SOURCE":"git@bitbucket.org:dy-devops/chef-dy-spark.git","COMMIT":"master","REPORT":"true","CONTEXT":"test"},"log":"","artifacts":{}}}'
    res=testee.parse_payload(body,{},querystring)
    self.assertEqual(res['name'], 'cookbook-test')
    self.assertEqual(res['done'], True)
    self.assertEqual(res['good'], True)
    self.assertEqual(res['report'], True)
    self.assertEqual(res['pr'], None)
    self.assertEqual(res['context'], 'test')
    self.assertEqual(res['source']['provider_url'], 'bitbucket.org')
    self.assertEqual(res['source']['organization'], 'dy-devops')
    self.assertEqual(res['source']['name'], 'chef-dy-spark')
    self.assertEqual(res['source']['commit'], 'master')
    self.assertEqual(res['target'], None)
    self.assertEqual(res['url'], 'http://build1.use.dynamicyield.com:8080/job/cookbook-test/3885/')
