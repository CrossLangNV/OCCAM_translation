import argparse

import sys

from translate_xml import XMLTranslator


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Translate an XML')

    parser.add_argument('filepath', metavar='xml', type=str,
                        help='filepath to xml file')

    parser.add_argument('source', type=str,
                        help='source language')

    parser.add_argument('target', type=str,
                        help='target language')

    parser.add_argument('b_textline', type=str2bool,
                        default=False,
                        help='Also translalte textlines')

    args = sys.argv[1:]

    if len(args) == 0:
        # Test script
        rel_path = 'multilingual_pageXML/user_scripts/translate_pagexml/output/multilingual_base.xml'
        args = ['../../' + rel_path, 'fr', 'en', 'True']

    args = parser.parse_args(args)

    foo = XMLTranslator(args.filepath, args.source)
    foo.translate(args.target, args.b_textline)
