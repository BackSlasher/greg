import unittest
from mock import MagicMock
from greg.provider import BridgeProvider
import os
import json

class TestProvider(unittest.TestCase):

    # Helper for testing
    def get_testee(self):
        testee = BridgeProvider({
            'username': 'greg',
            'password': 'grog',
            'incoming_token': 'glig',
            })
        return testee

    def test_text_filter_me_fine(self):
        testee = self.get_testee()
        testee.get_my_username = lambda: 'greg'
        inp = 'hello @greg'
        out = testee.text_filter_me(inp)
        self.assertEqual(out,'hello ')

    def test_text_filter_me_too_big(self):
        testee = self.get_testee()
        testee.get_my_username = lambda: 'greg'
        inp = 'hello @greg-gregor'
        out = testee.text_filter_me(inp)
        self.assertEqual(out,inp)

    def test_text_filter_me_too_small(self):
        testee = self.get_testee()
        testee.get_my_username = lambda: 'greg-gregor'
        inp = 'hello @greg'
        out = testee.text_filter_me(inp)
        self.assertEqual(out,inp)
