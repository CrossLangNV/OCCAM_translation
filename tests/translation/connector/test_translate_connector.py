"""
Swagger at https://mtapi.occam.crosslang.com/swagger-ui.html
"""

import os
import random
import signal
import string
import tempfile
import time
import unittest

import requests

from translation.connector.cef_etranslation import ETranslationConnector

ROOT_MEDIA = os.path.join(os.path.dirname(__file__), '../../media')

FILENAME_TXT = os.path.join(ROOT_MEDIA,
                            'CLARIAH-VL_examples/1KBR/De_Standaard_19190401/PERO_OCR/KB_JB840_1919-04-01_01_0.txt')
FILENAME_XML = os.path.join(ROOT_MEDIA,
                            'CLARIAH-VL_examples/1KBR/De_Standaard_19190401/PERO_OCR/KB_JB840_1919-04-01_01_0_fixed.xml')

FILENAME_BRIS_XML = os.path.join(ROOT_MEDIA, 'BRIS/20091542_p001.xml')

for filename in [FILENAME_TXT, FILENAME_XML, FILENAME_BRIS_XML]:
    assert os.path.exists(filename), 'Sanity check'


class TestTimeout(Exception):
    pass


class test_timeout:
    """
    To timeout methods if taking too long
    """

    def __init__(self, seconds, error_message=None):
        if error_message is None:
            error_message = 'test timed out after {}s.'.format(seconds)
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TestTimeout(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)


class TestETranslationConnector(unittest.TestCase):

    def setUp(self) -> None:
        self.connector = ETranslationConnector()

    def test_info(self):

        r = requests.get(self.connector.url_info)
        with self.subTest('Status code'):
            self.assertLess(r.status_code, 300)

        j = self.connector.info()

        with self.subTest('Non-empty'):
            self.assertTrue(j)

        with self.subTest('Password'):
            self.assertEqual('***', j.get("etranslation_password"), 'Password should not be publically visible!')

        return

    def test_trans_snippet(self):

        source = 'fr'
        target = 'en'
        snippet = 'This is a test sentence.'

        request_id = self.connector.trans_snippet(source, target, snippet)

        self.assertIsInstance(request_id, str)

        return

    def test_trans_snippet_id(self):

        i = '96659360'

        j = self.connector.trans_snippet_id(i)

        self.assertIsNotNone(j, 'Should be non-empty')

        return

    def test_trans_snippet_and_result(self):

        source = 'fr'
        target = 'en'
        # snippet = 'This is a test sentence.'
        # snippet =
        snippet = random_text_generator(15)

        request_id = self.connector.trans_snippet(source, target, snippet)

        t0 = time.time()
        delta_t_max = 10  # in seconds
        i = 0
        while True:

            r = self.connector.trans_snippet_id(request_id)
            i += 1
            if r is not None:
                break

            if time.time() - t0 > delta_t_max:
                # Took too long
                break

        t1 = time.time()
        print(f"Took {t1 - t0} before translation finished.")
        print(f"#Requests = {i}.")

        # r = self.connector.trans_snippet_id(request_id)

        self.assertIsNotNone(r, 'Should be non-empty')

        with self.subTest('Type'):
            self.assertIsInstance(r, str, f'Should contain translated text of "{snippet}"')

    def test_trans_snippet_blocking(self):

        source = 'fr'
        target = 'en'
        snippet = 'This is a test sentence.'

        t0 = time.time()
        snippet_trans = self.connector.trans_snippet_blocking(source, target, snippet)
        t1 = time.time()
        print(f"Took {t1 - t0} before translation finished.")

        self.assertIsInstance(snippet_trans, str)

        return

    def test_is_there_a_TM(self):

        source = 'fr'
        target = 'en'

        snippet = random_text_generator(5000)

        t0 = time.time()
        snippet_trans = self.connector.trans_snippet_blocking(source, target, snippet)
        t1 = time.time()

        print(f"Took {t1 - t0:.2f} s before translation finished.")

        t0 = time.time()
        snippet_trans = self.connector.trans_snippet_blocking(source, target, snippet)
        t1 = time.time()

        print(f"Took {t1 - t0:.2f} s before translation finished.")

        t0 = time.time()
        snippet_trans = self.connector.trans_snippet_blocking(source, target, snippet)
        t1 = time.time()

        print(f"Took {t1 - t0:.2f} s before translation finished.")

    def test_trans_doc(self):

        source = 'fr'
        target = 'en'

        request_id = self.connector.trans_doc(source, target, FILENAME_TXT)

        self.assertIsInstance(request_id, str)

    def test_trans_doc_id(self):
        i = '96678284'

        r = self.connector.trans_doc_id(i)

        self.assertIsNotNone(r, 'Should be non-empty')

        filename = r.get('filename')

        with tempfile.TemporaryDirectory() as tmp:
            path_filename = os.path.join(tmp, filename)

            with open(path_filename, 'wb') as f:
                f.write(r.get('content'))

            print(f'File temporarily saved to {path_filename}')

            with open(path_filename) as f:
                txt = f.readlines()

        return

    def test_trans_doc_blocking(self):

        source = 'fr'
        target = 'en'

        with open(FILENAME_TXT) as f:
            txt_orig = f.readlines()

        r = self.connector.trans_doc_blocking(source, target, FILENAME_TXT)

        self.assertIsNotNone(r, 'Should be non-empty')

        filename = r.get('filename')

        with tempfile.TemporaryDirectory() as tmp:
            tmp_filename = os.path.join(tmp, filename)

            with open(tmp_filename, 'wb') as f:
                f.write(r.get('content'))

            print(f'File temporarily saved to {tmp_filename}')

            with open(tmp_filename) as f:
                txt_trans = f.readlines()

        len(txt_trans)

        self.assertEqual(len(txt_orig), len(txt_trans),
                         "After translation, amount of text lines should stay the same as it's translated per line.")

        return


class TestTransXML(unittest.TestCase):
    """
    XML's will only work if they are valid. I.e. that they give are valid with respect to their schemes.
    """

    def setUp(self) -> None:
        self.connector = ETranslationConnector()

    def test_trans_doc_blocking(self):
        source = 'fr'
        target = 'en'

        # This file doesn't seem to work

        with open(FILENAME_BRIS_XML) as f:
            xml_orig = f.readlines()

        r = self.connector.trans_doc_blocking(source, target, FILENAME_BRIS_XML)

        self.assertIsNotNone(r, 'Should be non-empty')

        filename = r.get('filename')

        with tempfile.TemporaryDirectory() as tmp:
            tmp_filename = os.path.join(tmp, filename)

            with open(tmp_filename, 'wb') as f:
                f.write(r.get('content'))

            print(f'File temporarily saved to {tmp_filename}')

            with open(tmp_filename) as f:
                xml_trans = f.readlines()

        # len(txt_trans)

        # self.assertEqual(len(txt_orig), len(txt_trans),
        #                  "After translation, amount of text lines should stay the same as it's translated per line.")

        return


class TestKBR(unittest.TestCase):
    """
    Test the translation on real data from KBR
    """

    def setUp(self) -> None:
        self.connector = ETranslationConnector()

    def test_translate(self):
        source = 'nl'
        target = 'en'

        r = self.connector.trans_doc_blocking(source, target, FILENAME_XML)

        r.get('content')

        filename_trans = os.path.splitext(FILENAME_XML)[0] + f'_{source}_{target}.xml'

        folder = os.path.split(filename_trans)[0]
        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(filename_trans, 'wb') as f:
            f.write(r.get('content'))


def random_text_generator(n: int):
    return "".join([random.choice(string.ascii_letters[:26] + ' ' * 10) for i in range(n)])


if __name__ == '__main__':
    unittest.main()
