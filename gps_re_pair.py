#!/usr/bin/env python
"""
Try to detect & fix pairs of same-named exported JPGs where one has broken GPS
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pyexiv2

import gps_peek

Rational = Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]

IPTC_KEY_SUBJECT = 'Iptc.Application2.ObjectName'
IPTC_KEY_KEYWORDS = 'Iptc.Application2.Keywords'
GPS_LOCATION_KEYWORD = 'Approximate GPS location'

exif_keys = gps_peek.exif_keys


def parse_cli_args() -> argparse.Namespace:
    """
    Specify and parse command-line arguments

    Returns:
        Namespace of provided arguments
    """
    parser = argparse.ArgumentParser(
        description='Try to detect & fix pairs of same-named exported JPGs where one has broken GPS',
    )
    parser.add_argument('dir', help='Directory containing files to process')
    args = parser.parse_args()
    return args


def extract_image_id_from_filename(basename: str) -> Optional[str]:
    """
    Pull the initial numeric fragment from a filename, ignoring anything after brackets
    :param basename:
    :return:
    """
    match = re.match(r'[^(\d]*(\d+)', basename)
    return None if match is None else match.group(1)


def run_cli() -> None:
    """
    Execute the script according to CLI args
    :return:
    """
    args = parse_cli_args()

    img_sets: Dict[str, Dict[str, List[Path]]] = {}

    for source_file in list(Path(args.dir).glob('*.jpg')):
        basename = source_file.name
        image_id = extract_image_id_from_filename(basename)
        if image_id is None:
            continue

        if image_id not in img_sets:
            img_sets[image_id] = {'raw': [], 'derived': []}

        img_sets[image_id]['raw' if is_from_raw_file(source_file) else 'derived'].append(source_file)

    for img_set in img_sets.values():
        if len(img_set['raw']) > 0 and len(img_set['derived']) > 0:
            gps_source_file = img_set['raw'][0]

            print(f'Copy GPS from {gps_source_file} to: ', end='')
            good_gps = get_gps_from_file(gps_source_file)
            for derived in img_set['derived']:
                apply_exif_to_file(good_gps, derived)
                print(f'{derived}, ', end='')
                if 'fixed-gps' not in derived.name:
                    new_filename = derived.with_name(f'{derived.stem}-fixed-gps{derived.suffix}')
                    derived.rename(new_filename)
            print()

            if 'gps-donor' not in gps_source_file.name:
                new_filename = gps_source_file.with_name(f'{gps_source_file.stem}-gps-donor{gps_source_file.suffix}')
                gps_source_file.rename(new_filename)


def is_from_raw_file(img_path) -> bool:
    """
    Determine if an image file declares its RawFileName
    :param img_path:
    :return:
    """
    image = pyexiv2.Image(str(img_path))
    xmp = image.read_xmp()
    has_raw = len(xmp['Xmp.crs.RawFileName']) > 0
    return has_raw


def get_gps_from_file(img_path: Path) -> Dict:
    """
    Fetch just exif GPS data from a file as a dictionary
    :param img_path:
    :return:
    """
    image = pyexiv2.Image(str(img_path))
    exif = image.read_exif()
    gps_exif = {k: v for k, v in exif.items() if k in exif_keys}
    return gps_exif


def apply_exif_to_file(exif_map: Dict, img_path: Path):
    """
    Save new exif data to a file and close it
    :param exif_map:
    :param img_path:
    :return:
    """
    image = pyexiv2.Image(str(img_path))
    image.modify_exif(exif_map)
    image.close()


if __name__ == '__main__':
    run_cli()
