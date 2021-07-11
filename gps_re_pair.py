#!/usr/bin/env python
"""
Try to detect & fix pairs of same-named exported JPGs where one has broken GPS
"""

import argparse
import re
from pathlib import Path
from typing import Dict, Tuple

import pyexiv2

Rational = Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]

IPTC_KEY_SUBJECT = 'Iptc.Application2.ObjectName'
IPTC_KEY_KEYWORDS = 'Iptc.Application2.Keywords'
GPS_LOCATION_KEYWORD = 'Approximate GPS location'

exif_keys = [
    'Exif.GPSInfo.GPSVersionID',
    'Exif.GPSInfo.GPSLatitudeRef',
    'Exif.GPSInfo.GPSLatitude',
    'Exif.GPSInfo.GPSLongitudeRef',
    'Exif.GPSInfo.GPSLongitude',
    'Exif.GPSInfo.GPSAltitudeRef',
    'Exif.GPSInfo.GPSAltitude',
    'Exif.GPSInfo.GPSTimeStamp',
    'Exif.GPSInfo.GPSSatellites',
    'Exif.GPSInfo.GPSMapDatum',
    'Exif.GPSInfo.GPSDateStamp',
]


def parse_cli_args() -> argparse.Namespace:
    """
    Specify and parse command-line arguments

    Returns:
        Namespace of provided arguments
    """
    parser = argparse.ArgumentParser(
        description='Improve keywords and title organization for all images in a folder for upload to flickr, etc',
    )
    parser.add_argument('dir', help='Directory containing files to process')
    args = parser.parse_args()
    return args


def extract_image_id_from_filename(basename: str) -> str:
    """
    Pull the initial numeric fragment from a filename, ignoring anything after brackets
    NB: has issues with 1234-2 style, should only pick first digits
    :param basename:
    :return:
    """
    match = re.match(r'IMG_(\d{4})', basename)
    image_id = match.group(1)
    return image_id


def run_cli() -> None:
    """
    Execute the script according to CLI args
    :return:
    """
    args = parse_cli_args()

    img_sets = {}

    for source_file in list(Path(args.dir).glob('*.jpg')):
        basename = source_file.name
        image_id = extract_image_id_from_filename(basename)

        if image_id not in img_sets:
            img_sets[image_id] = {'raw': [], 'derived': []}

        img_sets[image_id]['raw' if is_from_raw_file(source_file) else 'derived'].append(source_file)

    for img_set_key in img_sets:
        img_set = img_sets[img_set_key]
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
    image = pyexiv2.Image(str(img_path))
    xmp = image.read_xmp()
    has_raw = len(xmp['Xmp.crs.RawFileName']) > 0
    return has_raw


def get_gps_from_file(img_path: Path) -> Dict:
    image = pyexiv2.Image(str(img_path))
    exif = image.read_exif()
    gps_exif = {k: v for k, v in exif.items() if k in exif_keys}
    return gps_exif


def apply_exif_to_file(exif_map: Dict, img_path: Path):
    image = pyexiv2.Image(str(img_path))
    image.modify_exif(exif_map)
    image.close()


if __name__ == '__main__':
    run_cli()
