import os
import sys
import unittest

from fastapi.testclient import TestClient
from lxml import etree

from api.main import app, _lookup_full_tm_match, _parse_text_page_xml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))

TEST_CLIENT = TestClient(app)

DIR_EXAMPLE_FILES = os.path.join(ROOT, 'tests/CEF-eTranslation_connector/example_files')


class TestApp(unittest.TestCase):
    def test_root(self):
        """ Test if root url can be accessed
        """

        response = TEST_CLIENT.get("/")

        self.assertLess(response.status_code, 300, "Status code should indicate a proper connection.")

    def test_docs(self):
        """ Test if open docs can be accessed
        """
        r = TEST_CLIENT.get('/docs')

        self.assertLess(r.status_code, 300, "Status code should indicate a proper connection.")


class TestTranslatePageXML(unittest.TestCase):
    def test_upload(self):
        path = os.path.join(ROOT,
                            'CLARIAH-VL_examples/1KBR/De_Standaard_19190401/PERO_OCR/KB_JB840_1919-04-01_01_0.xml')

        path_save = os.path.splitext(path)[0] + '_trans_multi.xml'

        with open(path, 'rb') as f:
            files = {'file': f}
            headers = {'source': 'nl',
                       'target': 'fr'}
            response = TEST_CLIENT.post("/translate/xml/blocking", files=files, headers=headers)

        with open(path_save, 'w') as f:
            f.write(response.text)

        self.assertLess(response.status_code, 300, "Status code should indicate a proper connection.")

    def test_upload_small(self):
        path = os.path.join(DIR_EXAMPLE_FILES,
                            'page_minimal_working_example.xml')

        path_multi_page = os.path.join(DIR_EXAMPLE_FILES,
                                       'multilingual_page_minimal_working_example.xml')

        path_save = os.path.join(DIR_EXAMPLE_FILES,
                                 'page_minimal_working_example_trans_multi.xml')

        with open(path, 'rb') as f:
            files = {'file': f}
            headers = {'source': 'fr',
                       'target': 'en'}
            response = TEST_CLIENT.post("/translate/xml/blocking", files=files, headers=headers)

        self.assertLess(response.status_code, 300, "Status code should indicate a proper connection.")

        with open(path_save, 'w') as f:
            f.write(response.text)

        s_multi_page_trans = response.text
        l_s_multi_page_trans = s_multi_page_trans.splitlines()

        with open(path_multi_page, 'r') as f:
            s_baseline = f.read()
        l_s_baseline = s_baseline.splitlines()

        s_multi_page_trans_single = _single_line_html(l_s_multi_page_trans)
        s_baseline_single = _single_line_html(l_s_baseline)

        with self.subTest('tree equal'):
            def get_text(el):
                text = el.text
                if text is not None:
                    return text.strip()

            def check_tree_equal(tree_i, tree_j):

                if get_text(tree_i) != get_text(tree_j):
                    # Could be a slightly different translation
                    if 'target' not in tree_i.tag:
                        # print('text')

                        self.fail(f'Text not the same: {get_text(tree_i)} != {get_text(tree_j)}')

                # if tree_i.attrib != tree_j.attrib:
                #     print('attrib')
                self.assertEqual(tree_i.attrib, tree_j.attrib)

                # if tree_i.tag != tree_j.tag:
                #     print('tag')
                self.assertEqual(tree_i.tag, tree_j.tag)

                for child_i, child_j in zip(tree_i.getchildren(), tree_j.getchildren()):
                    check_tree_equal(child_i, child_j)

            tree_trans = etree.fromstring(s_multi_page_trans_single.encode('utf-8'))
            tree_base = etree.fromstring(s_baseline_single.encode('utf-8'))

            check_tree_equal(tree_trans, tree_base)

        if 0:  # Not using this atm
            with self.subTest('string equal'):

                assert 0

                maxDiff = self.maxDiff
                self.maxDiff = None
                try:
                    self.assertEqual(s_multi_page_trans_single,
                                     s_baseline_single,
                                     'Strings should be equal')
                except Exception as e:
                    print(s_multi_page_trans)
                    print(s_baseline)

                    tb = sys.exc_info()[2]
                    raise e.with_traceback(tb)

                finally:
                    self.maxDiff = maxDiff

        if 0:
            for baseline_i, multi_page_trans_i in zip(l_s_baseline, l_s_multi_page_trans):
                with self.subTest('Compare lines {i}'):
                    if 1:  # Ignore indendation
                        self.assertEqual(baseline_i.strip(), multi_page_trans_i.strip())
                    else:
                        self.assertEqual(baseline_i, multi_page_trans_i)

    def test_upload_same_source_target_lang(self):
        path = os.path.join(DIR_EXAMPLE_FILES,
                            'page_minimal_working_example.xml')
        with open(path, 'rb') as f:
            files = {'file': f}
            headers = {'source': 'en',
                       'target': 'en'}
            response = TEST_CLIENT.post("/translate/xml/blocking", files=files, headers=headers)

        # TODO correct response
        self.assertEqual(response.status_code, 301, "Should indicate when source and target are the same.")


class TestTranslatePageXMLNonBlocking(unittest.TestCase):

    def test_get_xmls(self):
        response = TEST_CLIENT.get("/translate/xmls/",
                                   # files=files,
                                   # headers=headers
                                   )

        self.assertLess(response.status_code, 300)

    def test_upload(self):
        path = os.path.join(ROOT,
                            'CLARIAH-VL_examples/1KBR/De_Standaard_19190401/PERO_OCR/KB_JB840_1919-04-01_01_0.xml')

        with open(path, 'rb') as f:
            files = {'file': f}
            headers = {'source': 'nl',
                       'target': 'fr'}
            response = TEST_CLIENT.post("/translate/xml",
                                        files=files,
                                        headers=headers
                                        )

        self.assertLess(response.status_code, 300, "Status code should indicate a proper connection.")
        self.assertIn('id', response.json(), "Should contain the id.")

    def test_read(self):

        path = os.path.join(ROOT,
                            'CLARIAH-VL_examples/1KBR/De_Standaard_19190401/PERO_OCR/KB_JB840_1919-04-01_01_0.xml')

        with open(path, 'rb') as f:
            files = {'file': f}
            headers = {'source': 'nl',
                       'target': 'fr'}
            response = TEST_CLIENT.post("/translate/xml",
                                        files=files,
                                        headers=headers
                                        )

        id_trans = response.json()['id']

        import time
        t0 = time.time()
        t_max = 120  # seconds
        while time.time() - t0 < t_max:
            response = TEST_CLIENT.get(f"/translate/xml/{id_trans}",
                                       )
            if response.ok:
                break

            time.sleep(1)

        self.assertLess(response.status_code, 300, "Status code should indicate a proper connection.")
        self.assertTrue(response.content, "Should contain the xml.")

    def test_upload_small(self):

        path = os.path.join(DIR_EXAMPLE_FILES,
                            'page_minimal_working_example.xml')

        with open(path, 'rb') as f:
            files = {'file': f}
            headers = {'source': 'fr',
                       'target': 'en'}
            response = TEST_CLIENT.post("/translate/xml",
                                        files=files,
                                        headers=headers
                                        )

        self.assertLess(response.status_code, 300, "Status code should indicate a proper connection.")
        self.assertIn('id', response.json(), "Should contain the id.")

    def test_read_small(self):

        path = os.path.join(DIR_EXAMPLE_FILES,
                            'page_minimal_working_example.xml')

        with open(path, 'rb') as f:
            files = {'file': f}
            headers = {'source': 'fr',
                       'target': 'en'}
            response = TEST_CLIENT.post("/translate/xml",
                                        files=files,
                                        headers=headers
                                        )

        id_trans = response.json()['id']

        import time
        t0 = time.time()
        t_max = 120  # seconds
        while time.time() - t0 < t_max:
            response = TEST_CLIENT.get(f"/translate/xml/{id_trans}",
                                       )
            if response.ok:
                break

            time.sleep(1)

        self.assertLess(response.status_code, 300, "Status code should indicate a proper connection.")
        self.assertTrue(response.content, "Should contain the xml.")

        s_multi_page_trans = response.text

        tree_base = _get_tree_base()

        def get_B(s_multi_page_trans):

            l_s_multi_page_trans = s_multi_page_trans.splitlines()
            s_multi_page_trans_single = _single_line_html(l_s_multi_page_trans)
            tree_trans = etree.fromstring(s_multi_page_trans_single.encode('utf-8'))
            return tree_trans

        tree_trans = get_B(s_multi_page_trans)

        with self.subTest('tree equal'):
            self._check_tree_equal(tree_trans, tree_base)

    def _check_tree_equal(self, tree_i, tree_j):
        if _get_text(tree_i) != _get_text(tree_j):
            # Could be a slightly different translation
            if 'target' not in tree_i.tag:
                # print('text')

                self.fail(f'Text not the same: {_get_text(tree_i)} != {_get_text(tree_j)}')

        if tree_i.attrib != tree_j.attrib:
            print('attrib')
        self.assertEqual(tree_i.attrib, tree_j.attrib)

        if tree_i.tag != tree_j.tag:
            print('tag')
        self.assertEqual(tree_i.tag, tree_j.tag)

        for child_i, child_j in zip(tree_i.getchildren(), tree_j.getchildren()):
            self._check_tree_equal(child_i, child_j)


def _single_line_html(l,
                      b_replace_quote=True):
    s = ''
    for s_i in l:
        s_i = s_i.strip()

        if b_replace_quote:
            s_i = s_i.replace("'", '"')

        s += s_i
        if s[-1] != '>':
            s += ' '

    return s


def _get_text(el):
    text = el.text
    if text is not None:
        return text.strip()


def _get_tree_base():
    path_multi_page = os.path.join(DIR_EXAMPLE_FILES,
                                   'multilingual_page_minimal_working_example.xml')

    with open(path_multi_page, 'r') as f:
        s_baseline = f.read()
    l_s_baseline = s_baseline.splitlines()

    s_baseline_single = _single_line_html(l_s_baseline)
    tree_base = etree.fromstring(s_baseline_single.encode('utf-8'))
    return tree_base


class TestParseXMLTextLines(unittest.TestCase):

    def test_lookup_full_tm_match(self):
        full_match = _lookup_full_tm_match('this is a test', 'en-nl')
        print(full_match)
        return full_match

    def test_parse_text_page_xml(self):
        lines = ['this', 'this is a', 'this is a test']
        db_xml_document = _parse_text_page_xml(lines, 'en', 'nl')
        for db_line in db_xml_document.lines:
            print(db_line.text)
        return db_xml_document


if __name__ == '__main__':
    unittest.main()
