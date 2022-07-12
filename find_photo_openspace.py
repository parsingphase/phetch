#!/usr/bin/env python

"""
Find location names for images in a directory. Run with --help for details
"""

import argparse
from pathlib import Path
from typing import List, Optional

from iptcinfo3 import IPTCInfo

import piexif
from gps_tools import (EPSG_DATUM, ShapefileLocationFinder,
                       lng_lat_point_from_lat_lng,
                       load_custom_gpsvisualizer_polys_from_dir,
                       make_openspace_tag, match_openspace_tag)
from metadata_tools.iptc_utils import (mute_iptcinfo_logger,
                                       remove_iptcinfo_backup)
from metadata_tools.piexif_utils import get_decimal_lat_long_from_piexif

from shapefile_list import shapefiles

POLYDIR = 'polyfiles'

mute_iptcinfo_logger()


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

    polygons = load_custom_gpsvisualizer_polys_from_dir(POLYDIR)

    for image in source_files:
        place = None
        image_file = str(image)
        iptc = IPTCInfo(image_file)
        tag = iptc_get_openspace_tag(iptc)
        if tag:
            print(f'{image_file} already tagged ({tag})')
            continue
        exif_dict = piexif.load(image_file)  # type: ignore
        lat_lng = get_decimal_lat_long_from_piexif(exif_dict)
        if not lat_lng:
            print(f'{image_file} has no GPS')
            continue

        lng_lat_point = lng_lat_point_from_lat_lng(lat_lng)
        for named_poly in polygons:
            if named_poly['polygon'].contains(lng_lat_point):
                place = named_poly['name']
                print(f'Found {image_file} in {place} polyfile')
                break

        if not place:
            for shape in shapefiles:
                finder = ShapefileLocationFinder(shape['filename'], shape['name_field'])
                place = finder.place_from_lat_lng(lng_lat_point)
                if place:
                    finder_name = shape['name']
                    print(f'Found {image_file} in {finder_name} finder')
                    break

        print(image.name, lat_lng, place)
        if place:
            add_place_tag_to_file_iptc(iptc, place)
            remove_iptcinfo_backup(image_file)


def add_place_tag_to_file_iptc(iptc, place) -> None:
    """
    Add a place name as a machine tag to the passed IPTC handler and save
    Args:
        iptc:
        place:

    Returns:

    """
    tags = decode_tags(iptc)
    place_tag = make_openspace_tag(place)
    if place_tag not in tags:
        iptc['keywords'] += [place_tag.encode('utf-8')]
        iptc.save()


def decode_tags(iptc) -> List[str]:
    """
    Extract keyword tags from IPTC handler and decode from bytes to utf-8
    Args:
        iptc:

    Returns:

    """
    raw_tags = iptc['keywords']
    tags = [k.decode('utf-8') for k in raw_tags]
    return tags


def iptc_get_openspace_tag(iptc) -> Optional[str]:
    """
    Extract a recognized place machine tag, if any, from IPTC handler
    Args:
        iptc:

    Returns:

    """
    tags = decode_tags(iptc)
    openspace_tags = [t for t in tags if match_openspace_tag(t)]
    return openspace_tags[0] if len(openspace_tags) > 0 else None


if __name__ == '__main__':
    run_cli()
