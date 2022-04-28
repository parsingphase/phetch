#!/usr/bin/env python

"""
Improve keywords and title organization for all images in a folder for upload to flickr, etc
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from iptcinfo3 import IPTCInfo
from PIL import Image

import piexif
from metadata_tools.iptc_utils import (mute_iptcinfo_logger,
                                       remove_iptcinfo_backup)
from metadata_tools.piexif_utils import (get_date_taken,
                                         get_decimal_lat_long_from_piexif,
                                         get_piexif_dms_from_decimal)

Rational = Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]

GPS_LOCATION_KEYWORD = 'Approximate GPS location'

mute_iptcinfo_logger()


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


def extract_image_id_from_filename(basename: str) -> Optional[str]:
    """
    Pull the initial numeric fragment from a filename, ignoring anything after brackets
    :param basename:
    :return:
    """
    match = re.match(r'^\S{4}(\d{4})', basename)
    return None if match is None else match.group(1)


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
            if isinstance(value, list):  # strictly, any iterable, but we should only see lists
                changed = (len(set(value) - set(original[key])) + len(set(original[key]) - set(value))) > 0
            else:
                changed = original[key] != revised[key]
        else:
            changed = True

        if changed:
            break

    return changed


def remove_title_blocklist_keywords(keywords: List[str]) -> List[str]:
    """
    Remove keywords that tend not to indicate a species name / valid title
    """
    blocklist = [
        'Maine', 'Massachusetts', 'export', 'pelagic', 'TakenByEva', 'flash', 'Rhode Island', 'Connecticut',
        'Cyanocitta cristata', 'unknown', 'Larinae',
        'juvenile',
        'unidentified', 'scenic', 'Cambridge', 'Boston', GPS_LOCATION_KEYWORD
    ]
    up_blocklist = [k.upper() for k in blocklist]
    keywords = [k for k in keywords if k.upper() not in up_blocklist]
    return keywords


def find_subject_from_keywords(keywords: List[str]) -> Optional[str]:
    """
    Find the longest usable keyword in a list for use as a subject
    Args:
        keywords:

    Returns:

    """
    keywords = [k for k in keywords if ':' not in k]  # remove machine keywords
    keywords = remove_title_blocklist_keywords(keywords)  # remove blocklist
    longest_keyword = max(keywords, key=len) if len(keywords) > 0 else None
    return longest_keyword


def round_piexiv_gps(exif_dict, decimal_places) -> Optional[Dict]:
    """
    Round the GPS data (lat,lng) in the provided exif dict to the specified number of decimal places
    Args:
        exif_dict:
        decimal_places:

    Returns: Data changed if any

    """
    revised_exif = None
    lat_long_from_piexif = get_decimal_lat_long_from_piexif(exif_dict)
    if lat_long_from_piexif:
        lat, lng = lat_long_from_piexif
        round_lat, round_lng = (
            round(lat, decimal_places),
            round(lng, decimal_places)
        )
        if (round_lat != lat) or (round_lng != lng):
            revised_exif = get_piexif_dms_from_decimal((round_lat, round_lng))
    return revised_exif


def run_cli() -> None:
    """
    Execute the script according to CLI args
    :return:
    """
    args = parse_cli_args()

    for source_file in list(Path(args.dir).glob('*.jpg')):
        basename = source_file.name
        filename = str(source_file)
        exif_dict = piexif.load(filename)  # type: ignore
        revised_exif = None

        # Revise location if specified
        if args.gps_dp is not None and exif_dict is not None:
            revised_exif = round_piexiv_gps(exif_dict, args.gps_dp)

        # Now gather the keywords implied by the image location and data
        image_id = extract_image_id_from_filename(basename)
        serial_keyword = f'library:fileId={image_id}'
        if exif_dict is not None:
            date = get_date_taken(exif_dict)
            if date:
                serial_keyword += '-' + date.strftime('%Y%m%d')
        keywords = [serial_keyword]

        if revised_exif:
            for key in revised_exif:
                exif_dict[key] = revised_exif[key]

            keywords.append(GPS_LOCATION_KEYWORD)  # human-readable
            keywords.append(f'gps:accuracy={args.gps_dp}dp')
            # Save EXIF if changed
            exif_bytes = piexif.dump(exif_dict)  # type: ignore
            image = Image.open(filename)
            print('Save EXIF', exif_dict)
            image.save(filename, exif=exif_bytes)

        # Find and apply subjects and keywords
        iptc_changed = False
        iptc = IPTCInfo(filename)
        for keyword in keywords:
            existing_keywords = [k.decode('utf-8') for k in iptc['keywords']]
            if keyword not in existing_keywords:
                iptc['keywords'].append(keyword.encode('utf-8'))
                iptc_changed = True

        # Is there already a subject?
        subject = iptc['object name'].decode('utf-8') if iptc['object name'] else None
        if not subject:
            subject = find_subject_from_keywords([k.decode('utf-8') for k in iptc['keywords']])
            if subject:
                iptc['object name'] = subject.encode('utf-8')
                iptc_changed = True

        # Save IPTC if changed
        if iptc_changed:
            iptc.save()
            remove_iptcinfo_backup(filename)

        if args.rename:
            # If we can get a subject from revised or existing data, apply it to the name
            if subject and not re.search(r'\([^)]{3,}\)', basename):
                # FIXME: check that existing filename is not already present, use -N strategy if so
                new_filename = source_file.with_name(f'{source_file.stem} ({subject}){source_file.suffix}')
                source_file.rename(new_filename)
                print(f' Renamed {filename} to {new_filename}')


if __name__ == '__main__':
    run_cli()
