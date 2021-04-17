#!/usr/bin/env python
"""
Improve keywords and title organization for all images in a folder for upload to flickr, etc
"""

import argparse
import re
from pathlib import Path
from typing import Dict, Optional, Set, Tuple, cast

import pyexiv2

Rational = Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]

IPTC_KEY_SUBJECT = 'Iptc.Application2.ObjectName'
IPTC_KEY_KEYWORDS = 'Iptc.Application2.Keywords'
EXIF_KEY_LATITUDE = 'Exif.GPSInfo.GPSLatitude'
EXIF_KEY_LONGITUDE = 'Exif.GPSInfo.GPSLongitude'
GPS_LOCATION_KEYWORD = 'Approximate GPS location'


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
    tuples = cast(Rational, tuple(tuple(int(n) for n in p.split('/')) for p in parts))
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


def round_gps_location(exif, gps_dp: int) -> Dict:
    """
    Take the GPS EXIF data from the supplied image and rounds its lat/long to the specified number of decimal points
    :param exif:
    :param gps_dp:
    :return:
    """
    revised_location = {}
    if EXIF_KEY_LATITUDE not in exif or EXIF_KEY_LATITUDE not in exif:
        return {}

    lat = exif[EXIF_KEY_LATITUDE]
    lon = exif[EXIF_KEY_LONGITUDE]

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


def extract_iptc_keywords(iptc: Dict) -> Set[str]:
    """
    Get keywords from IPTC data as a list
    :param iptc:
    :return:
    """
    keywords = ()
    if IPTC_KEY_KEYWORDS in iptc:
        keywords = iptc[IPTC_KEY_KEYWORDS]
        if not isinstance(keywords, list):
            keywords = [keywords]

    return set(keywords)


def extract_image_id_from_filename(basename: str) -> str:
    """
    Pull the initial numeric fragment from a filename, ignoring anything after brackets
    :param basename:
    :return:
    """
    image_id = re.sub(r'[^\d]|(\(.*)', '', basename)
    return image_id


def populated_keys_changed(original: Dict, revised: Dict) -> bool:
    """
    Check whether any of the keys in revised changed from original
    :param original:
    :param revised:
    :return:
    """
    changed = False

    for (key, value) in revised.items():
        if key in original:
            if type(value) == list:
                changed = len(set(value) - set(original[key])) > 0
            else:
                changed = original[key] != revised[key]
        else:
            changed = True
            break

    return changed


def revise_iptc(iptc, additional_keywords: Optional[Set] = None) -> Dict:
    """
    Regenerated IPTC data based on keywords and subject
    additional_keywords will not be considered as candidates for subject
    :param iptc:
    :param additional_keywords:
    :return:
    """
    if additional_keywords is None:
        additional_keywords = ()

    revised_iptc = {}

    # Update image properties to/from keywords
    keywords = extract_iptc_keywords(iptc)
    non_machine_keywords = [k for k in keywords if ':' not in k and k != GPS_LOCATION_KEYWORD]
    if IPTC_KEY_SUBJECT not in iptc:
        longest_keyword = max(non_machine_keywords, key=len)
        if longest_keyword:
            subject = make_subject(longest_keyword)
            revised_iptc[IPTC_KEY_SUBJECT] = subject

    keywords = keywords.union(set(additional_keywords))

    if len(keywords) > 0:
        revised_iptc[IPTC_KEY_KEYWORDS] = list(keywords)

    return revised_iptc


def save_revised_image(image, basename: str, revised_exif: Dict, revised_iptc: Dict):
    """
    Store any changed data to the image at the provided location
    :param image:
    :param basename:
    :param revised_exif:
    :param revised_iptc:
    :return:
    """
    if len(revised_iptc.keys()) > 0:
        image.modify_iptc(revised_iptc)
        print(f'Revised IPTC for {basename}', revised_iptc)
    if len(revised_exif.keys()) > 0:
        image.modify_exif(revised_exif)
        print(f'Revised EXIF for {basename}', revised_exif)


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

        exif = image.read_exif()
        revised_exif = {}

        # Revise location if specified
        if args.gps_dp is not None:
            revised_exif = round_gps_location(exif, args.gps_dp)

        # Now gather the keywords implied by the image location and data
        image_id = extract_image_id_from_filename(basename)
        keywords = [f'library:fileId={image_id}']

        if populated_keys_changed(exif, revised_exif):
            keywords.append(GPS_LOCATION_KEYWORD)  # human-readable
            keywords.append(f'gps:accuracy={args.gps_dp}dp')

        # Find and apply subjects and keywords
        iptc = image.read_iptc()
        keywords = set(keywords)  # normalize
        revised_iptc = revise_iptc(iptc, keywords)

        if populated_keys_changed(exif, revised_exif) or populated_keys_changed(iptc, revised_iptc):
            # We don't want to update (and change timestamp) if nothing changed
            save_revised_image(image, basename, revised_exif, revised_iptc)
        image.close()

        if args.rename:
            # If we can get a subject from revised or existing data, apply it to the name
            subject = revised_iptc.get(IPTC_KEY_SUBJECT, iptc.get(IPTC_KEY_SUBJECT, None))
            if subject and '(' not in basename:
                new_filename = source_file.with_name(f'{source_file.stem} ({subject}){source_file.suffix}')
                source_file.rename(new_filename)
                print(f' Renamed {filename} to {new_filename}')


if __name__ == '__main__':
    run_cli()
