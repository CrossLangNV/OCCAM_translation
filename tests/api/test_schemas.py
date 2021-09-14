import unittest

from app.schemas import XMLDocumentLineBase


class TestXMLDocumentLineBase(unittest.TestCase):
    def test_keys(self):
        full_match = 'Test match'
        text = 'Test text'
        obj = XMLDocumentLineBase(text=text,
                                  full_match=full_match)

        with self.subTest('Text'):
            self.assertEqual(obj.text, text)

        with self.subTest('Match'):
            self.assertEqual(obj.full_match, full_match)
