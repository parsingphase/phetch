#!/usr/bin/env python
"""
Fetch one or more Flickr albums. Run with --help for details
"""

import argparse
from pathlib import Path
import piexif
from gps_tools.piexif_utils import get_clean_lat_long_from_piexif
from gps_tools import find_lat_lng_shapefile_place

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
    for image in source_files:
        exif_dict = piexif.load(str(image))
        lat_lng = get_clean_lat_long_from_piexif(exif_dict)
        place = find_lat_lng_shapefile_place(lat_lng, SHAPEFILE) if lat_lng else None
        print(image.name, lat_lng, place)


if __name__ == '__main__':
    run_cli()
