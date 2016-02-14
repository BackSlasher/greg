# testing greg.builder.jenkins

import unittest

class TestBridgeBuilderJenkins(unittest.TestCase):
  # parse_repo parses git@bla urls
  def test_parse_repo(self):
    from greg.builder.jenkins import BridgeBuilderJenkins
    testee = BridgeBuilderJenkins({
        'url':'http://wow.com',
        'username': 'greg',
        'password': 'grog',
        'incoming_token': 'hi',
        })
    res=testee.parse_repo('git@bla.com:blu/bli.git')
    self.assertEqual(res[0],'git@bla.com:')
    self.assertEqual(res[1],'blu')
    self.assertEqual(res[2],'bli')

  def recurse_sort_xml(self,a):
    import xml.etree.ElementTree as ET
    a.tail=''
    if len(a): a.text='' # Remove leftover text if this node has child elements
    children = [ c for c in  a ]
    # TODO will it keep them alive?
    for child in children:
      a.remove(child)
      self.recurse_sort_xml(child)
    sorted_children = sorted(children, key=lambda item: ET.tostring(item))
    for child in sorted_children:
      a.append(child)

  def assertXmlEqual(self,a,b):
    import xml.etree.ElementTree as ET
    clone_a = ET.fromstring(ET.tostring(a))
    clone_b = ET.fromstring(ET.tostring(b))
    self.recurse_sort_xml(clone_a)
    self.recurse_sort_xml(clone_b)
    self.assertEqual(ET.tostring(clone_a), ET.tostring(clone_b))

  # parse_payload works with exmaple data
  def test_parse_payload(self):
    from greg.builder.jenkins import BridgeBuilderJenkins
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
    self.assertEqual(res['source']['provider_url'], 'git@bitbucket.org:')
    self.assertEqual(res['source']['organization'], 'dy-devops')
    self.assertEqual(res['source']['name'], 'chef-dy-spark')
    self.assertEqual(res['source']['commit'], 'master')
    self.assertEqual(res['target'], None)
    self.assertEqual(res['url'], 'http://build1.use.dynamicyield.com:8080/job/cookbook-test/3885/')

  def test_ensure_notification_endpoint_notouch(self):
    from greg.builder.jenkins import BridgeBuilderJenkins
    import xml.etree.ElementTree as ET
    testee = BridgeBuilderJenkins({
        'url':'http://wow.com',
        'username': 'greg',
        'password': 'grog',
        'incoming_token': 'hi',
        })
    xml_config = '''
<project><properties>
<com.tikal.hudson.plugins.notification.HudsonNotificationProperty plugin="notification@1.9">
      <endpoints>
        <com.tikal.hudson.plugins.notification.Endpoint>
          <protocol>HTTP</protocol>
          <format>JSON</format>
          <url>http://good-url.com/build?builder=jenkins&amp;token=hi</url>
          <event>completed</event>
          <timeout>30000</timeout>
          <loglines>0</loglines>
        </com.tikal.hudson.plugins.notification.Endpoint>
        <com.tikal.hudson.plugins.notification.Endpoint>
          <protocol>HTTP</protocol>
          <format>JSON</format>
          <url>http://requestb.in/15rhdx23</url>
          <event>all</event>
          <timeout>30000</timeout>
          <loglines>0</loglines>
        </com.tikal.hudson.plugins.notification.Endpoint>
      </endpoints>
</com.tikal.hudson.plugins.notification.HudsonNotificationProperty>
</properties></project>
'''
    config_before = ET.fromstring(xml_config)
    config_after = ET.fromstring(xml_config)
    testee.ensure_notification_endpoint('http://good-url.com/build?builder=jenkins&token=hi',config_after)
    self.assertXmlEqual(config_before, config_after)

  def test_ensure_notification_endpoint_add(self):
    from greg.builder.jenkins import BridgeBuilderJenkins
    import xml.etree.ElementTree as ET
    testee = BridgeBuilderJenkins({
        'url':'http://wow.com',
        'username': 'greg',
        'password': 'grog',
        'incoming_token': 'hi',
        })
    config_before = ET.fromstring('''
<project><properties>
<com.tikal.hudson.plugins.notification.HudsonNotificationProperty plugin="notification@1.9">
      <endpoints>
        <com.tikal.hudson.plugins.notification.Endpoint>
          <protocol>HTTP</protocol>
          <format>JSON</format>
          <url>http://localhost:8081/jenkins?token=5QIGCvBLv0sZ7cRUOr55</url>
          <event>completed</event>
          <timeout>30000</timeout>
          <loglines>0</loglines>
        </com.tikal.hudson.plugins.notification.Endpoint>
        <com.tikal.hudson.plugins.notification.Endpoint>
          <protocol>HTTP</protocol>
          <format>JSON</format>
          <url>http://requestb.in/15rhdx23</url>
          <event>all</event>
          <timeout>30000</timeout>
          <loglines>0</loglines>
        </com.tikal.hudson.plugins.notification.Endpoint>
      </endpoints>
</com.tikal.hudson.plugins.notification.HudsonNotificationProperty>
</properties></project>
''')
    config_proper = ET.fromstring('''
<project><properties>
<com.tikal.hudson.plugins.notification.HudsonNotificationProperty plugin="notification@1.9">
      <endpoints>
        <com.tikal.hudson.plugins.notification.Endpoint>
          <protocol>HTTP</protocol>
          <format>JSON</format>
          <url>http://localhost:8081/jenkins?token=5QIGCvBLv0sZ7cRUOr55</url>
          <event>completed</event>
          <timeout>30000</timeout>
          <loglines>0</loglines>
        </com.tikal.hudson.plugins.notification.Endpoint>
        <com.tikal.hudson.plugins.notification.Endpoint>
          <protocol>HTTP</protocol>
          <format>JSON</format>
          <url>http://requestb.in/15rhdx23</url>
          <event>all</event>
          <timeout>30000</timeout>
          <loglines>0</loglines>
        </com.tikal.hudson.plugins.notification.Endpoint>
        <com.tikal.hudson.plugins.notification.Endpoint>
          <protocol>HTTP</protocol>
          <format>JSON</format>
          <url>http://good-url.com/build?builder=jenkins&amp;token=hi</url>
          <event>completed</event>
          <timeout>30000</timeout>
          <loglines>0</loglines>
        </com.tikal.hudson.plugins.notification.Endpoint>
      </endpoints>
</com.tikal.hudson.plugins.notification.HudsonNotificationProperty>
</properties></project>
''')
    testee.ensure_notification_endpoint('http://good-url.com/build?builder=jenkins&token=hi',config_before)
    self.assertXmlEqual(config_before, config_proper)
