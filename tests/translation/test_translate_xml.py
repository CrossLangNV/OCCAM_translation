import os
import tempfile
import unittest
import warnings

from lxml import etree
from xml_orm.orm import PageXML

from translation.connector.cef_etranslation import ETranslationConnector

CEF_LOGIN = os.environ.get("CEF_LOGIN")
CEF_PASSW = os.environ.get("CEF_PASSW")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
FOLDER_EXAMPLE_FILES = os.path.join(ROOT, 'tests/media/example_files')

FILENAME_OVERLAY = os.path.join(FOLDER_EXAMPLE_FILES, 'overlay_working.xml')
FILENAME_OVERLAY_SMALL = os.path.join(FOLDER_EXAMPLE_FILES, 'overlay_working_small.xml')

FILENAME_KBR_XML = os.path.join(ROOT,
                                'tests/media/CLARIAH-VL_examples/1KBR/De_Standaard_19190401/PERO_OCR/KB_JB840_1919-04-01_01_0_fixed.xml')

warnings.warn('This set of tests are deprecated since it is not advised to translate the xml directly!', UserWarning)


class TestTranslateXML(unittest.TestCase):

    def setUp(self) -> None:
        self.connector = ETranslationConnector(CEF_LOGIN, CEF_PASSW)

    def test_translate_working_small(self):
        FILENAME = os.path.join(FOLDER_EXAMPLE_FILES,
                                'overlay_working_small.xml'
                                )

        SOURCE = 'NL'
        TARGET = 'EN'

        r = self.connector.trans_doc_blocking(SOURCE,
                                              TARGET,
                                              FILENAME
                                              )

        self.assertTrue(r.get('content'))

    def test_translate_failing_small(self):
        """ It is important that there is an xml declaration

        :return:
        """

        SOURCE = 'NL'
        TARGET = 'EN'

        for filename in [FILENAME_OVERLAY,
                         FILENAME_OVERLAY_SMALL]:
            with self.subTest(os.path.split(filename)[-1]):
                r = self.connector.trans_doc_blocking(SOURCE,
                                                      TARGET,
                                                      filename,
                                                      )

                content = r.get('content')
                self.assertTrue(content)

                xml_base = PageXML(filename)
                xml_base.validate()

                xml = _get_xml_from_content(content)

                print(etree.dump(xml_base.element_tree.getroot()))
                print(etree.dump(xml.element_tree.getroot()))

                with self.subTest('Validation should fail on the date.'):
                    self.assertRaises(Exception, xml.validate)

    def test_translate_header(self):
        """
        We might have to be careful that the header is translated
        :return:
        """

        FILENAME = os.path.join(FOLDER_EXAMPLE_FILES,
                                'page_minimal_working_example.xml'
                                )

        SOURCE = 'EN'
        TARGET = 'FR'

        r = self.connector.trans_doc_blocking(SOURCE,
                                              TARGET,
                                              FILENAME
                                              )

        content = r.get('content')
        self.assertTrue(content)

        xml_base = PageXML(FILENAME)
        xml_base.validate()

        xml = _get_xml_from_content(content)

        root = xml.element_tree.getroot()

        root_base = xml_base.element_tree.getroot()

        nsmap = root.nsmap
        PAGE_NAMESPACE = nsmap.get(None)

        def _get_tag(tag):
            return f'{{{PAGE_NAMESPACE}}}{tag}'

        METADATA_TAG = _get_tag("Metadata")
        c_meta = root.findall(METADATA_TAG)[0].getchildren()

        c_meta_root = root_base.findall(METADATA_TAG)[0].getchildren()

        self.assertGreaterEqual(len(c_meta), 1, 'Sanity check, should be non-empty')
        self.assertEqual(len(c_meta), len(c_meta_root), 'Should contain the same amount of child elements')

        for c_meta_i, c_meta_root_i in zip(c_meta, c_meta_root):
            with self.subTest(c_meta_i):
                self.assertEqual(c_meta_i.text, c_meta_root_i.text)

    def test_translate(self):

        SOURCE = 'NL'
        TARGET = 'EN'

        FILENAME_TRANS = os.path.splitext(FILENAME_KBR_XML)[0] + f'_{SOURCE}_{TARGET}.xml'

        r = self.connector.trans_doc_blocking(SOURCE,
                                              TARGET,
                                              FILENAME_KBR_XML
                                              )

        self.assertTrue(r.get('content'))

        with self.subTest('Exporting'):
            with open(FILENAME_TRANS, 'bw') as f:
                f.write(r.get('content'))

    def test_valid_xml_after_translation(self):

        SOURCE = 'NL'
        TARGET = 'EN'

        for name in ['pero_ocr_overlay1.xml',
                     'pero_ocr_overlay_small1.xml']:
            with self.subTest(name):
                FILENAME = os.path.join(FOLDER_EXAMPLE_FILES,
                                        name
                                        )

                r = self.connector.trans_doc_blocking(SOURCE,
                                                      TARGET,
                                                      FILENAME
                                                      )

                content = r.get('content')

                with tempfile.TemporaryDirectory() as dir:
                    name_trans = os.path.splitext(name)[0] + f'_{SOURCE}_{TARGET}.xml'

                    filename_trans = os.path.join(dir, name_trans)

                    with open(filename_trans, 'wb') as f:
                        f.write(content)

                    xml_base = PageXML(FILENAME)

                    xml = PageXML(filename_trans)

                    with self.subTest('Sanity check'):
                        try:
                            xml_base.validate()
                        except Exception:
                            self.fail("validate raised Exception unexpectedly!")

                    b = 0
                    if b:  # Debugging
                        print(etree.dump(xml_base.element_tree.getroot()))
                        print(etree.dump(xml.element_tree.getroot()))

                    with self.subTest('Validation (Ignore atm)'):
                        try:
                            xml.validate()
                        except Exception:
                            self.fail("validate raised Exception unexpectedly!")


def _get_xml_from_content(content):
    with tempfile.TemporaryDirectory() as d:
        filename_trans = os.path.join(d, 'tmp.xml')

        with open(filename_trans, 'wb') as f:
            f.write(content)

        xml = PageXML(filename_trans, b_autofix=True)

        return xml
