import os
import warnings

from lxml import etree

from connector.translate_connector import translate_text, translate_xliff


class XMLTranslator(object):
    def __init__(self, filepath, source):
        """
        Prepares for translating from source to a target language
        by using CEF AT eTranslation service.

        Args:
            filepath: path to xml file
            source: source language of xml file
        """

        self.filepath = filepath
        self.source = source

    def translate(self, target, b_textline, b_save=True):
        """
        Read xml and translate XLIFF trans-unit nodes.
        Translated xml file is saved in same folder as file
        as <fileroot>_<source>-<target>.xml

        Args:
            target: target language to translate to
            b_textline: bool to decide if textlines should also be translated

        Returns:
            translated xml in lxml tree format
        """

        tree = etree.parse(self.filepath)

        list_trans_unit = tree.xpath('''//*[name()='TextRegion']/*[name()='TextEquiv']//*[name()='trans-unit']/..''')
        for i, trans_unit in enumerate(list_trans_unit):
            print(f'Text region: {i + 1}/{len(list_trans_unit)}')

            self._translate_trans_unit(trans_unit, target)

        if b_textline:
            list_trans_unit = tree.xpath('''//*[name()='TextLine']/*[name()='TextEquiv']//*[name()='trans-unit']/..''')
            for i, trans_unit in enumerate(list_trans_unit):
                print(f'Text line: {i + 1}/{len(list_trans_unit)}')

                self._translate_trans_unit(trans_unit, target)

        if b_save:
            root, _ = os.path.splitext(self.filepath)
            filepath_out = root + f'_{self.source}-{target}.xml'

            tree.write(filepath_out, pretty_print=True, encoding='utf-8')

        return tree

    def _translate_trans_unit(self, trans_unit, target):
        """
        Sends xml with <trans-unit/> to translation controller and updates xml node.
        Args:
            trans_unit: lxml node with containting a <trans-unit/> node
            target: target language to translate to

        Returns:

        """
        # For each TextRegion
        parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')

        s_trans_unit = etree.tostring(trans_unit)
        try:
            s_trans_unit_translated = translate_xliff(s_trans_unit, self.source, target).encode('utf-8')

        except Exception:
            print('Failed to get translation. Skipping')

            return -1

        trans_unit_translated = etree.fromstring(s_trans_unit_translated, parser=parser)

        trans_unit.getparent().replace(trans_unit, trans_unit_translated)


def tree_transunit_source_text_translation_iter(tree, source, target):
    """

    Returns:

    """

    warnings.warn('No need to work with text when you can send in xliff for translation',
                  DeprecationWarning)

    for node_source in tree.xpath('''//*trans-unit/*[name()='source']'''):
        text = node_source.text

        translated_text = translate_text(text, source, target)

        yield translated_text
