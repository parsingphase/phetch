#!/usr/bin/env python
"""
Check raw GPS info for given files
"""

import argparse
from pathlib import Path

import pyexiv2

from phetch_tools import GPS

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

xmp_keys = [
    'Xmp.xmpMM.History',  # prints as 'type="Seq"', doesn't appear iterable
    'Xmp.xmpMM.History[1]/stEvt:action',  # derived / edited / saved - derived means a conversion
    'Xmp.xmpMM.History[1]/stEvt:parameters',  # 'converted from image/x-canon-cr3 to image/tiff, saved to new location'
    'Xmp.crs.RawFileName',
]


def parse_cli_args() -> argparse.Namespace:
    """
    Specify and parse command-line arguments

    Returns:
        Namespace of provided arguments
    """
    parser = argparse.ArgumentParser(
        description='Check raw GPS data of specified files',
    )
    parser.add_argument('files', nargs='+', help='Files to examine')

    args = parser.parse_args()
    return args


def run_cli() -> None:
    """
    Execute the script according to CLI args
    :return:
    """
    args = parse_cli_args()
    files = args.files

    for file in files:
        s = '         As float:'
        pathed_file = Path(file)
        filename = str(pathed_file)
        image = pyexiv2.Image(filename)

        exif = image.read_exif()
        xmp = image.read_xmp()
        # if we have Xmp.crs.RawFileName it's from a RAW not a TIFF
        # print(".\n".join(xmp.keys()))

        print(file)
        print('=' * 60)
        for key in exif_keys:
            try:
                exif_value = exif[key]
            except KeyError:
                exif_value = ' [N/A] '

            print(f'{key:30} {exif_value}')
            if key in ['Exif.GPSInfo.GPSLatitude', 'Exif.GPSInfo.GPSLongitude']:
                float_val = GPS.exif_rational_dms_to_float(GPS.string_to_exif_rational(exif_value))
                print(f'{s:30} {float_val}')
                # Lat:  +/- 90
                # Long: +/- 80

        for xkey in xmp_keys:
            try:
                xmp_value = xmp[xkey]
                xmp_count = len(xmp_value)
            except KeyError:
                xmp_value = ' [N/A] '

            print(f'{xkey:30} {xmp_value} / {xmp_count}')

        print()


if __name__ == '__main__':
    run_cli()
