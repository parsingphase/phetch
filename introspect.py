#!/usr/bin/env python
"""
Improve keywords and title organization for all images in a folder for upload to flickr, etc
"""

import argparse
import re
from pathlib import Path
from typing import Tuple

import pyexiv2

Rational = Tuple[Tuple[int]]

IPTC_KEY_SUBJECT = 'Iptc.Application2.ObjectName'
IPTC_KEY_KEYWORDS = 'Iptc.Application2.Keywords'
EXIF_KEY_LATITUDE = 'Exif.GPSInfo.GPSLatitude'
EXIF_KEY_LONGITUDE = 'Exif.GPSInfo.GPSLongitude'


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
    parser.add_argument('--rename', help='Modify filename to include subject', action='store_true')
    parser.add_argument('--gps-dp', help='Number of decimal places to fuzz GPS location to', type=int)
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


def string_to_exif_rational(text: str) -> Rational:
    """
    Given a Rational exif string, eg 71/1 81159000/10000000 0/1, unpack to (2-3) Tuple of (nom,denom)

    :param text:
    :return:
    """
    parts = text.split(' ')
    tuples = tuple([tuple([int(n) for n in p.split('/')]) for p in parts])
    return tuples


def exif_rational_dms_to_float(dms: Rational) -> float:
    """
    Given a Rational of Degrees, Minutes, Seconds, convert it to a float
    :param dms:
    :return:
    """
    float_parts = [v[0] / v[1] for v in dms]
    float_out = sum([float_parts[i] / pow(60, i) for i in range(0, len(float_parts))])
    return float_out


def degrees_float_to_dms_rational_string(degrees: float):
    minutes_dp = 6
    (int_degrees, frac_degrees) = [int(p) for p in str(degrees).split('.')]
    minutes = round(float(f'0.{frac_degrees}') * 60, minutes_dp)
    denominator = pow(10, minutes_dp)
    numerator = int(minutes * denominator)
    return f'{int_degrees}/1 {numerator}/{denominator} 0/1'


def round_gps_location(image, gps_dp: int):
    revised_location = {}
    exif = image.read_exif()
    lat = exif[EXIF_KEY_LATITUDE]
    lon = exif[EXIF_KEY_LONGITUDE]
    print(f'lat "{lat}"')
    print(f'lon "{lon}"')

    if lat:
        revised_location[EXIF_KEY_LATITUDE] = round_dms_as_decimal(lat, gps_dp)

    if lon:
        revised_location[EXIF_KEY_LONGITUDE] = round_dms_as_decimal(lon, gps_dp)

    return revised_location


def round_dms_as_decimal(dms, gps_dp):
    old_lat = exif_rational_dms_to_float(string_to_exif_rational(dms))
    new_lat = round(old_lat, gps_dp)
    new_lat_string = degrees_float_to_dms_rational_string(new_lat)
    return new_lat_string


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

        revised_exif = {}
        if args.gps_dp is not None:
            revised_exif = round_gps_location(image, args.gps_dp)

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

        if revised_exif.keys():
            image.modify_exif(revised_exif)
            print(f'Revised EXIF for {basename}', revised_exif)

        image.close()

        if args.rename:
            if subject and '(' not in basename:
                new_filename = source_file.with_name(f'{source_file.stem} ({subject}){source_file.suffix}')
                source_file.rename(new_filename)
                print(f' Renamed {filename} to {new_filename}')


def extract_image_id_from_filename(basename: str) -> str:
    """
    Pull the initial numeric fragment from a filename, ignoring anything after brackets
    :param basename:
    :return:
    """
    image_id = re.sub(r'[^\d]|(\(.*)', '', basename)
    return image_id


if __name__ == '__main__':
    run_cli()
