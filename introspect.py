#!/usr/bin/env python
"""
Improve keywords and title organization for all images in a folder for upload to flickr, etc
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple, cast

import pyexiv2

Rational = Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]

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
    # cast = 'Trust me on the length!'
    tuples = cast(Rational, tuple([tuple([int(n) for n in p.split('/')]) for p in parts]))
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
    """
    Convert a float value to an EXIF degrees, minutes, seconds rational string

    :param degrees:
    :return:
    """
    minutes_dp = 6
    (int_degrees, frac_degrees) = [int(p) for p in str(degrees).split('.')]
    minutes = round(float(f'0.{frac_degrees}') * 60, minutes_dp)
    denominator = pow(10, minutes_dp)
    numerator = int(minutes * denominator)
    return f'{int_degrees}/1 {numerator}/{denominator} 0/1'


def round_gps_location(image, gps_dp: int) -> Dict:
    """
    Take the GPS EXIF data from the supplied image and rounds its lat/long to the specified number of decimal points
    :param image:
    :param gps_dp:
    :return:
    """
    revised_location = {}
    exif = image.read_exif()
    if EXIF_KEY_LATITUDE not in exif or EXIF_KEY_LATITUDE not in exif:
        return {}

    lat = exif[EXIF_KEY_LATITUDE]
    lon = exif[EXIF_KEY_LONGITUDE]
    print(f'lat "{lat}"')
    print(f'lon "{lon}"')

    if lat:
        revised_location[EXIF_KEY_LATITUDE] = round_dms_as_decimal(lat, gps_dp)

    if lon:
        revised_location[EXIF_KEY_LONGITUDE] = round_dms_as_decimal(lon, gps_dp)

    return revised_location


def round_dms_as_decimal(dms: str, gps_dp: int) -> str:
    """
    Take an EXIF Rational DMS string, round it as a float of degrees, and re-encode it
    :param dms:
    :param gps_dp:
    :return:
    """
    old_lat = exif_rational_dms_to_float(string_to_exif_rational(dms))
    new_lat = round(old_lat, gps_dp)
    new_lat_string = degrees_float_to_dms_rational_string(new_lat)
    return new_lat_string


def extract_iptc_keywords(iptc: Dict) -> List[str]:
    """
    Get keywords from IPTC data as a list
    :param iptc:
    :return:
    """
    keywords = []
    if IPTC_KEY_KEYWORDS in iptc:
        keywords = iptc[IPTC_KEY_KEYWORDS]
        if not isinstance(keywords, list):
            keywords = [keywords]
    return keywords


def extract_image_id_from_filename(basename: str) -> str:
    """
    Pull the initial numeric fragment from a filename, ignoring anything after brackets
    :param basename:
    :return:
    """
    image_id = re.sub(r'[^\d]|(\(.*)', '', basename)
    return image_id


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

        # Revise location if specified
        geo_exif = {}
        if args.gps_dp is not None:
            geo_exif = round_gps_location(image, args.gps_dp)
            if len(geo_exif.keys()) == 0:
                print(f'No geo data in {filename}')

        # Update image properties to/from keywords
        image_id = extract_image_id_from_filename(basename)

        iptc = image.read_iptc()
        revised_iptc = {}

        keywords = extract_iptc_keywords(iptc)
        keywords.append(f'library:fileId={image_id}')

        non_machine_keywords = [k for k in keywords if ':' not in k]

        subject = ''
        if IPTC_KEY_SUBJECT in iptc:
            # Leave existing subjects alone
            subject = iptc[IPTC_KEY_SUBJECT]
        elif non_machine_keywords:
            longest_keyword = max(non_machine_keywords, key=len)
            if longest_keyword:
                revised_iptc[IPTC_KEY_SUBJECT] = subject = make_subject(longest_keyword)

        # Add some informational keywords if we modified GPS
        if geo_exif is not None:
            keywords.append('Approximate GPS location')
            keywords.append(f'gps:accuracy={args.gps_dp}dp')

        if len(keywords) > 0:
            revised_iptc[IPTC_KEY_KEYWORDS] = list(set(keywords))  # set removes dups

        save_revised_image(image, basename, geo_exif, revised_iptc)
        image.close()

        if args.rename:
            if subject and '(' not in basename:
                new_filename = source_file.with_name(f'{source_file.stem} ({subject}){source_file.suffix}')
                source_file.rename(new_filename)
                print(f' Renamed {filename} to {new_filename}')


def save_revised_image(image, basename: str, revised_exif: Dict, revised_iptc: Dict):
    """
    Store any changed data to the image at the provided location
    :param image:
    :param basename:
    :param revised_exif:
    :param revised_iptc:
    :return:
    """
    if revised_iptc.keys():
        image.modify_iptc(revised_iptc)
        print(f'Revised IPTC for {basename}', revised_iptc)
    if revised_exif.keys():
        image.modify_exif(revised_exif)
        print(f'Revised EXIF for {basename}', revised_exif)


if __name__ == '__main__':
    run_cli()
