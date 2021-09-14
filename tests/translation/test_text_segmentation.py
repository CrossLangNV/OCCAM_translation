import os
import unittest

from xml_orm.orm import PageXML

from translation.translate_xml import translate_list, SentenceParser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
ROOT_MEDIA = os.path.join(ROOT, 'tests/media')

FILENAME_CLARIAH_XML = os.path.join(ROOT_MEDIA,
                                    'CLARIAH-VL_examples/1KBR/De_Standaard_19190401/PERO_OCR/KB_JB840_1919-04-01_01_0_fixed.xml')


class TestLineJoiner(unittest.TestCase):
    def test_foo(self):
        source = 'nl'

        xml_orm = PageXML(FILENAME_CLARIAH_XML)

        lines = xml_orm.get_lines_text()

        parser = SentenceParser(xml_orm)
        l_region_sentences = parser.get_region_sentences()

        sentences = parser.get_sentences()

        if 0:
            sentences_trans = translate_list(sentences, 'nl', 'en')
            parser.reconstruct_lines(sentences_trans)

        region_lines_new = parser.reconstruct_lines(sentences)

        n_region_new = [sum(map(len, region)) + len([line for line in region if line]) - 1 for region in
                        region_lines_new]

        n_region_old = list(map(len, xml_orm.get_regions_text()))

        for i, (n_new, n_old) in enumerate(zip(n_region_new, n_region_old)):
            with self.subTest(i):
                self.assertEqual(n_new, n_old)
