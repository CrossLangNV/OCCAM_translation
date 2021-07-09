import os
from os import close
from unittest import TestCase

from tm.tm_connector import MouseTmConnector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
FILENAME_TMX = 'examples_data/en-nl_min.tmx'


class MouseTmConnectorTest(TestCase):

    def setUp(self):
        self.conn = MouseTmConnector()

    def test_health(self):
        response = self.conn.health_check()
        print(response.content)
        self.assertEqual(response.status_code, 200)

    def test_lookup_tu(self):
        matches = self.conn.lookup_tu(False, '', 'en-nl', 'this is a test')
        print(matches)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["match"], 1.0)
        self.assertEqual(matches[0]["segment"], 'this is a test')
        self.assertEqual(matches[0]["translation"], 'dit is een test')

    def test_add_tu(self):
        response = self.conn.add_tu('', 'en-nl', 'this is a test', 'dit is een test')
        print(response.content)
        self.assertEqual(response.status_code, 200)

    def test_delete_tu(self):
        response = self.conn.delete_tu('', 'en-nl', 'this is a test', 'dit is een test')
        print(response.content)
        self.assertEqual(response.status_code, 200)

    def test_import_tmx(self):
        with open(FILENAME_TMX, 'rb') as tmx:
            response = self.conn.import_tmx('', 'en-nl', tmx)
            print(response.content)
            self.assertEqual(response.status_code, 202)

    def test_get_tu_amount(self):
        response = self.conn.get_tu_amount('', 'en-nl')
        print(response)
        self.assertGreaterEqual(response, 0)
