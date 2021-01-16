#!/usr/bin/env python
"""
Improve image's keywords and title organization for upload to flickr, etc
"""

import argparse
import re
from pathlib import Path

import pyexiv2

IPTC_KEY_SUBJECT = 'Iptc.Application2.ObjectName'
IPTC_KEY_KEYWORDS = 'Iptc.Application2.Keywords'


def parse_cli_args() -> argparse.Namespace:
    """
    Specify and parse command-line arguments

    Returns:
        Namespace of provided arguments
    """
    parser = argparse.ArgumentParser(
        description='Improve image\'s keywords and title organization for upload to flickr, etc',
    )
    parser.add_argument('dir', help='Directory containing files to watermark')
    args = parser.parse_args()
    return args


def uc_first(text: str):
    """
    Upper-case first letter of a non-empty string
    :param text:
    :return:
    """
    if text:
        text = text[0].upper() + text[1:]
    return text


def make_subject(text: str):
    """
    Format a string into a suitably-capitalized subject
    :param text:
    :return:
    """
    if not re.match('/[A-Z]/', text):
        text = ' '.join([uc_first(part) for part in text.split(' ')])
    return text


def run_cli() -> None:
    """
    Execute the script according to CLI args
    :return:
    """
    args = parse_cli_args()
    source_dir = Path(args.dir.rstrip('/'))

    source_files = list(source_dir.glob('*.jpg'))
    for source_file in source_files:
        basename = source_file.name
        image = pyexiv2.Image(str(source_file))
        iptc = image.read_iptc()

        image_id = int(re.sub(r'[^\d]', '', basename))

        revised_iptc = {}

        keywords = []
        if IPTC_KEY_KEYWORDS in iptc:
            keywords = iptc[IPTC_KEY_KEYWORDS]
            if not isinstance(keywords, list):
                keywords = [keywords]

        keywords.append(f'library:fileId={image_id}')
        keywords = list(set(keywords))  # make unique
        revised_iptc[IPTC_KEY_KEYWORDS] = keywords
        non_machine_keywords = [k for k in keywords if ':' not in k]

        if IPTC_KEY_SUBJECT in iptc:
            # Leave existing subjects alone
            pass
        else:
            longest_keyword = max(non_machine_keywords, key=len)
            if longest_keyword:
                revised_iptc[IPTC_KEY_SUBJECT] = make_subject(longest_keyword)

        image.modify_iptc(revised_iptc)
        print(f'Revised IPTC for {basename}', revised_iptc)


if __name__ == '__main__':
    run_cli()
