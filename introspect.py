#!/usr/bin/env python
"""
Improve keywords and title organization for all images in a folder for upload to flickr, etc
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
        description='Improve keywords and title organization for all images in a folder for upload to flickr, etc',
    )
    parser.add_argument('dir', help='Directory containing files to watermark')
    parser.add_argument('--rename', help='Modify filename to include subject', action='store_true')
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

    for source_file in list(Path(args.dir).glob('*.jpg')):
        basename = source_file.name
        filename = str(source_file)
        image = pyexiv2.Image(filename)
        iptc = image.read_iptc()

        image_id = extract_image_id_from_filename(basename)

        revised_iptc = {}

        keywords = []
        if IPTC_KEY_KEYWORDS in iptc:
            keywords = iptc[IPTC_KEY_KEYWORDS]
            if not isinstance(keywords, list):
                keywords = [keywords]

        file_id_keyword = f'library:fileId={image_id}'

        if file_id_keyword not in keywords:
            keywords.append(file_id_keyword)
            revised_iptc[IPTC_KEY_KEYWORDS] = keywords

        non_machine_keywords = [k for k in keywords if ':' not in k]

        subject = ''
        if IPTC_KEY_SUBJECT in iptc:
            # Leave existing subjects alone
            subject = iptc[IPTC_KEY_SUBJECT]
        elif non_machine_keywords:
            longest_keyword = max(non_machine_keywords, key=len)
            if longest_keyword:
                revised_iptc[IPTC_KEY_SUBJECT] = subject = make_subject(longest_keyword)

        if revised_iptc.keys():
            image.modify_iptc(revised_iptc)
            print(f'Revised IPTC for {basename}', revised_iptc)
        image.close()

        if args.rename:
            if subject and '(' not in basename:
                new_filename = source_file.with_name(f'{source_file.stem} ({subject}){source_file.suffix}')
                source_file.rename(new_filename)
                print(f' Renamed {filename} to {new_filename}')


def extract_image_id_from_filename(basename: str):
    """
    Pull the initial numeric fragment from a filename, ignoring anything after brackets
    :param basename:
    :return:
    """
    image_id = int(re.sub(r'[^\d]|(\(.*)', '', basename))
    return image_id


if __name__ == '__main__':
    run_cli()
