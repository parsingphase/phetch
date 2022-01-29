#!/usr/bin/env python
"""
Fetch one or more Flickr albums. Run with --help for details
"""

import argparse
import re
from pathlib import Path
import piexif
from gps_tools.piexif_utils import get_clean_lat_long_from_piexif
from gps_tools import ShapefileLocationFinder, EPSG_DATUM
from iptcinfo3 import IPTCInfo

import logging

iptcinfo_logger = logging.getLogger('iptcinfo')
iptcinfo_logger.setLevel(logging.ERROR)

SHAPEFILE = 'tmp/openspace/OPENSPACE_POLY'


def parse_cli_args() -> argparse.Namespace:
    """
    Specify and parse command-line arguments

    Returns:
        Namespace of provided arguments
    """
    parser = argparse.ArgumentParser(
        description='Find location names for images in a directory',
    )
    parser.add_argument('dir', help='Directory containing files to locate')
    args = parser.parse_args()
    # if not args.dir:
    #     raise "dir must be specified"
    return args


def run_cli() -> None:
    """
    Run the script from the CLI
    :return:
    """
    args = parse_cli_args()

    source_dir = Path(args.dir.rstrip('/'))

    source_files = list(source_dir.glob('*.jpg')) + list(source_dir.glob('*.jpeg'))

    finder = ShapefileLocationFinder(SHAPEFILE, EPSG_DATUM['NAD83'], 'SITE_NAME')

    for image in source_files:
        image_file = str(image)
        iptc = IPTCInfo(image_file)
        tag = iptc_get_openspace_tag(iptc)
        if tag:
            print(f'{image_file} already tagged ({tag})')
            continue
        exif_dict = piexif.load(image_file)
        lat_lng = get_clean_lat_long_from_piexif(exif_dict)
        place = finder.place_from_lat_lng(lat_lng) if lat_lng else None
        print(image.name, lat_lng, place)
        if place:
            add_place_tag_to_file_iptc(iptc, place)


def add_place_tag_to_file_iptc(iptc, place):
    tags = decode_tags(iptc)
    place_tag = f'geo:ma-openspace={place}'
    if not place_tag in tags:
        iptc['keywords'] += [place_tag.encode('utf-8')]
        iptc.save()


def decode_tags(iptc):
    raw_tags = iptc['keywords']
    tags = [k.decode('utf-8') for k in raw_tags]
    return tags


def iptc_get_openspace_tag(iptc):
    tags = decode_tags(iptc)
    openspace_tags = [t for t in tags if re.match(r'^geo:ma-openspace=', t)]
    return openspace_tags[0] if len(openspace_tags) > 0 else None


if __name__ == '__main__':
    run_cli()
