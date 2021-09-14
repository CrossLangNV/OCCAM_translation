import os
import tempfile
import warnings
from typing import List

from nltk.tokenize import sent_tokenize
from xml_orm.orm import OverlayXML

from .connector.cef_etranslation import ETranslationConnector


# class XMLTranslator(object):
#     def __init__(self, filepath, source):
#         """
#         Prepares for translating from source to a target language
#         by using CEF AT eTranslation service.
#
#         Args:
#             filepath: path to xml file
#             source: source language of xml file
#         """
#
#         self.filepath = filepath
#         self.source = source
#
#     def translate(self, target, b_textline, b_save=True):
#         """
#         Read xml and translate XLIFF trans-unit nodes.
#         Translated xml file is saved in same folder as file
#         as <fileroot>_<source>-<target>.xml
#
#         Args:
#             target: target language to translate to
#             b_textline: bool to decide if textlines should also be translated
#
#         Returns:
#             translated xml in lxml tree format
#         """
#
#         tree = etree.parse(self.filepath)
#
#         list_trans_unit = tree.xpath('''//*[name()='TextRegion']/*[name()='TextEquiv']//*[name()='trans-unit']/..''')
#         for i, trans_unit in enumerate(list_trans_unit):
#             print(f'Text region: {i + 1}/{len(list_trans_unit)}')
#
#             self._translate_trans_unit(trans_unit, target)
#
#         if b_textline:
#             list_trans_unit = tree.xpath('''//*[name()='TextLine']/*[name()='TextEquiv']//*[name()='trans-unit']/..''')
#             for i, trans_unit in enumerate(list_trans_unit):
#                 print(f'Text line: {i + 1}/{len(list_trans_unit)}')
#
#                 self._translate_trans_unit(trans_unit, target)
#
#         if b_save:
#             root, _ = os.path.splitext(self.filepath)
#             filepath_out = root + f'_{self.source}-{target}.xml'
#
#             tree.write(filepath_out, pretty_print=True, encoding='utf-8')
#
#         return tree
#
#     def _translate_trans_unit(self, trans_unit, target):
#         """
#         Sends xml with <trans-unit/> to translation controller and updates xml node.
#         Args:
#             trans_unit: lxml node with containting a <trans-unit/> node
#             target: target language to translate to
#
#         Returns:
#
#         """
#         # For each TextRegion
#         parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
#
#         s_trans_unit = etree.tostring(trans_unit)
#         try:
#             s_trans_unit_translated = translate_xliff(s_trans_unit, self.source, target).encode('utf-8')
#
#         except Exception:
#             print('Failed to get translation. Skipping')
#
#             return -1
#
#         trans_unit_translated = etree.fromstring(s_trans_unit_translated, parser=parser)
#
#         trans_unit.getparent().replace(trans_unit, trans_unit_translated)


class SentenceParser:
    def __init__(self, xml: OverlayXML):

        self.xml = xml

    def get_region_sentences(self,
                             b_assert=False):

        regions = self.xml.get_regions_text()

        l_region_sentences = []
        for region in regions:
            region_sentences = _get_sentences(region)
            l_region_sentences.append(region_sentences)

        if b_assert:  # Testing
            n_char_sentence = [[len(sent) for sent in region] for region in l_region_sentences]

            region_lines = self.xml.get_regions_lines_text()
            n_region_lines = [[len(l) for l in lines] for lines in region_lines]

            for i_region, (n_char, n_lines) in enumerate(zip(n_char_sentence, n_region_lines)):

                # Empty:
                if sum(n_char) == sum(n_lines) == 0:
                    continue

                d = sum(n_char) + len(n_char) - 1 - (sum(n_lines) + len(n_lines) - 1)
                if d != 0:
                    print(f'{i_region}. d = {d}')

        return l_region_sentences

    def get_sentences(self):

        sentences = [sent for reg_sent in self.get_region_sentences() for sent in reg_sent]

        return sentences

    def group_sentences_per_region(self, sentences):
        """
        Reverse operation: going from get_sentences() to get_region_sentences() again.
        """

        region_sentences_orig = self.get_region_sentences()
        assert len(sentences) == sum(len(sent_reg_orig) for sent_reg_orig in self.get_region_sentences()), \
            'Sentences should be matched'

        region_sentences = [[] for _ in region_sentences_orig]

        for i, sent_orig_i in enumerate(region_sentences_orig):
            region_sentences[i] = [sentences.pop(0) for _ in sent_orig_i]

        return region_sentences

    def reconstruct_lines(self, sentences: List[str]):
        """
        Tries to construct the sentences back as close to the original structure of the text lines.
        """

        region_sentences_orig = self.get_region_sentences()
        region_sentences = self.group_sentences_per_region(sentences)

        region_lines = self.xml.get_regions_lines_text()

        region_lines_new = [[]] * len(region_lines)

        for i_region, (sentences_region, sentences_region_orig, lines_region) in enumerate(
                zip(region_sentences, region_sentences_orig, region_lines)):

            sentences_region_copy = sentences_region[:]
            n_sent_reg_orig = list(map(len, sentences_region_orig))
            n_lines_region = list(map(len, lines_region))

            lines_region_new = [[] for _ in range(len(lines_region))]

            i_c_begin_line = 0
            i_c_begin_sent = 0

            for i_line, n_line in enumerate(n_lines_region):
                i_c_begin_line_next = i_c_begin_line + n_line + 1

                while i_c_begin_line <= i_c_begin_sent < i_c_begin_line_next:
                    if len(sentences_region_copy) == 0:
                        break

                    lines_region_new[i_line].append(sentences_region_copy.pop(0))
                    i_c_begin_sent_next = i_c_begin_sent + n_sent_reg_orig.pop(0) + 1
                    i_c_begin_sent = i_c_begin_sent_next

                i_c_begin_line = i_c_begin_line_next

            region_lines_new[i_region] = [' '.join(lines) for lines in lines_region_new]

            # TODO Cut a single sentence over multiple lines at the right place!

            pass

        return region_lines_new


def translate_list(l_text, source, target):
    # translation
    connector = ETranslationConnector()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = os.path.join(tmp_dir, 'tmp_text_lines.txt')
        s_tmp = ''.join(text_i + '\n' for text_i in l_text)
        with open(tmp_file, 'w') as f:
            f.write(s_tmp)
        # send to MT
        j = connector.trans_doc_blocking(source, target, tmp_file)

    l_trans_text = list(map(str.strip, j['content'].decode('UTF-8').splitlines()))

    return l_trans_text


def tree_transunit_source_text_translation_iter(tree, source, target):
    """

    Returns:

    """

    connector = ETranslationConnector()

    warnings.warn('No need to work with text when you can send in xliff for translation',
                  DeprecationWarning)

    for node_source in tree.xpath('''//*trans-unit/*[name()='source']'''):
        text = node_source.text

        translated_text = connector.trans_snippet_blocking(text, source, target)

        yield translated_text


def _get_sentences(text):
    return sent_tokenize(text)
