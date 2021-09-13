import os
from unittest import TestCase

from tm.tm_connector import MouseTmConnector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
FILENAME_TMX = 'examples_data/en-nl_min.tmx'


class MouseTmConnectorTest(TestCase):
    PAIR = 'en-nl'
    NL_SENT = 'dit is een test'
    EN_SENT = 'this is a test'

    def setUp(self):
        self.conn = MouseTmConnector()

        self.conn.add_tu('', self.PAIR, self.EN_SENT, self.NL_SENT)

    def tearDown(self) -> None:
        self.conn.delete_tu('', self.PAIR, self.EN_SENT, self.NL_SENT)

    def test_health(self):
        response = self.conn.health_check()
        print(response.content)
        self.assertEqual(response.status_code, 200)

    def test_lookup_tu(self):
        matches = self.conn.lookup_tu(False, '', self.PAIR, self.EN_SENT)
        print(matches)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["match"], 1.0)
        self.assertEqual(matches[0]["segment"], self.EN_SENT)
        self.assertEqual(matches[0]["translation"], self.NL_SENT)

    def test_add_tu(self):
        response = self.conn.add_tu('', self.PAIR, self.EN_SENT, self.NL_SENT)
        print(response.content)
        self.assertEqual(response.status_code, 200)

    def test_delete_tu(self):
        response = self.conn.delete_tu('', self.PAIR, self.EN_SENT, self.NL_SENT)
        print(response.content)
        self.assertEqual(response.status_code, 200)

    def test_import_tmx(self):
        with open(FILENAME_TMX, 'rb') as tmx:
            response = self.conn.import_tmx('', self.PAIR, tmx)
            print(response.content)
            self.assertEqual(response.status_code, 202)

    def test_get_tu_amount(self):
        response = self.conn.get_tu_amount('', self.PAIR)
        print(response)
        self.assertGreaterEqual(response, 0)
