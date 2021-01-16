#!/usr/bin/env python
"""
Improve image's keywords and title organization for upload to flickr, etc
"""

import argparse
from pathlib import Path

import pyexiv2

IPTC_KEY_SUBJECT='Iptc.Application2.ObjectName'
IPTC_KEY_KEYWORDS='Iptc.Application2.Keywords'

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


def run_cli():
    args = parse_cli_args()
    source_dir = Path(args.dir.rstrip('/'))

    i=0

    source_files = list(source_dir.glob('*.jpg'))
    for image in source_files:
        image_path = str(image)
        basename = image.name
        print(image_path)
        image = pyexiv2.Image(image_path)
        iptc = image.read_iptc()
        print(iptc)
        # print(image.read_exif())
        # 'Iptc.Application2.ObjectName': 'Black-capped Chickadee', 'Iptc.Application2.Keywords': ['black-capped chickadee']
        if IPTC_KEY_SUBJECT in iptc:
            print(f'{image_path} has subject "{iptc[IPTC_KEY_SUBJECT]}"')
        else:
            print(f'{image_path} has no subject')
            image.modify_iptc({IPTC_KEY_SUBJECT: basename})
        # image.modify_iptc({IPTC_KEY_SUBJECT: ''}) # to clear a field
        if IPTC_KEY_KEYWORDS in iptc:
            print(f'{image_path} has keywords "{iptc[IPTC_KEY_KEYWORDS]}"')




if __name__ == '__main__':
    run_cli()
