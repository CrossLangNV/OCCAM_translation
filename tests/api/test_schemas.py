import unittest

from api.schemas import XMLDocumentLineBase


class TestXMLDocumentLineBase(unittest.TestCase):
    def test_keys(self):
        match = 'Test match'
        text = 'Test text'
        obj = XMLDocumentLineBase(text=text,
                                  match=match)

        with self.subTest('Text'):
            self.assertEqual(obj.text, text)

        with self.subTest('Match'):
            self.assertEqual(obj.match, match)

