import io
import os
import unittest

from xml_orm.orm import PageXML, XLIFFPageXML

from translation.translate_xml import translate_list, SentenceParser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
ROOT_MEDIA = os.path.join(ROOT, 'tests/media')

FILENAME_CLARIAH_XML = os.path.join(ROOT_MEDIA,
                                    'CLARIAH-VL_examples/1KBR/De_Standaard_19190401/PERO_OCR/KB_JB840_1919-04-01_01_0_fixed.xml')

FILENAME_EXPORT_TEST = os.path.join(ROOT_MEDIA, 'delete_me.xml')


class TestLineJoiner(unittest.TestCase):

    def setUp(self) -> None:
        self.xml_orm = PageXML(FILENAME_CLARIAH_XML)

    def test_reconstruct_lines(self):
        lines = self.xml_orm.get_lines_text()

        parser = SentenceParser(self.xml_orm)
        l_region_sentences = parser.get_region_sentences()

        sentences = parser.get_sentences()

        region_lines_new = parser.reconstruct_lines(sentences)

        for i, (region_base, region_new) in enumerate(zip(self.xml_orm.get_regions_lines_text(), region_lines_new)):
            for j, (line_base, line_new) in enumerate(zip(region_base, region_new)):
                with self.subTest(f'{i} {j}:'):
                    self.assertEqual(len(line_base), len(line_new),
                                     f'Should have equal length: {line_base}!={line_new}')

        if 0:  # deprecated
            n_region_new = [sum(map(len, region)) + len([line for line in region if line]) - 1 for region in
                            region_lines_new]

            n_region_old = list(map(len, self.xml_orm.get_regions_text()))

            for i, (n_new, n_old) in enumerate(zip(n_region_new, n_region_old)):
                with self.subTest(i):
                    self.assertEqual(n_new, n_old)

    def test_split_up_after_reconstruction(self):
        baseline_region_lines = self.xml_orm.get_regions_lines_text()

        parser = SentenceParser(self.xml_orm)
        sentences = parser.get_sentences()
        region_lines_new = parser.reconstruct_lines(sentences)

        self.assertListEqual(baseline_region_lines[0], region_lines_new[0],
                             'Should split up again identical to original sentences.')

    def test_split_up_after_reconstruction_with_translation(self):

        source = 'nl'
        target = 'en'

        baseline_region_lines = self.xml_orm.get_regions_lines_text()

        parser = SentenceParser(self.xml_orm)
        sentences = parser.get_sentences()

        sentences_trans = translate_list(sentences, source, target)

        region_lines_new = parser.reconstruct_lines(sentences_trans)

        with self.subTest('Non-empty'):
            for baseline_lines_i, lines_new_i in zip(baseline_region_lines, region_lines_new):
                for baseline_line_j, line_new_j in zip(baseline_lines_i, lines_new_i):
                    if baseline_line_j:
                        self.assertTrue(line_new_j, f'Line should be non-empty if it was non-empty before.\n'
                                                    f'{baseline_line_j} -> {line_new_j}')

        s_all_trans = ' '.join(sentences_trans)
        s_all_reconstruct = ' '.join(line for reg in region_lines_new for line in reg)

        with self.subTest('the same (short)'):
            n = 200

            self.assertEqual(s_all_trans[:n], s_all_reconstruct[:n])

        with self.subTest('the same (all)'):

            self.assertEqual(s_all_trans, s_all_reconstruct)

        # parser = SentenceParser(self.xml_orm)
        # sentences = parser.get_sentences()
        # region_lines_new = parser.reconstruct_lines(sentences)
        #
        # self.assertListEqual(baseline_region_lines[0], region_lines_new[0], 'Should split up again identical to original sentences.')

    def test_reconstruct_translation(self):
        source = 'nl'
        target = 'en'

        parser = SentenceParser(self.xml_orm)

        sentences = parser.get_sentences()

        sentences_trans = translate_list(sentences, source, target)

        region_lines_new = parser.reconstruct_lines(sentences_trans)
        lines_new = [line for region in region_lines_new for line in region]

        with io.BytesIO(self.xml_orm.to_bstring()) as f:
            xml_trans = XLIFFPageXML.from_page(f, source)
        xml_trans.add_targets(lines_new, target)

        print(xml_trans.to_bstring())

        xml_trans.write(FILENAME_EXPORT_TEST)


class TestGroupSentencesPerRegion(unittest.TestCase):

    def setUp(self) -> None:
        self.xml_orm = PageXML(FILENAME_CLARIAH_XML)
        self.parser = SentenceParser(self.xml_orm)

    def test_equivalence(self):
        region_sentences = self.parser.get_region_sentences()
        sentences = self.parser.get_sentences()

        region_sentences_reverse = self.parser.group_sentences_per_region(sentences)

        self.assertEqual(region_sentences_reverse, region_sentences, 'Should reconstruct the same content.')
