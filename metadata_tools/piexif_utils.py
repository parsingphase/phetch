from datetime import datetime

from dateutil.parser import parse
from typing import Dict, Optional, Tuple

import piexif
from gps_tools.gps import GPS


def get_decimal_lat_long_from_piexif(exif_dict) -> Optional[Tuple[float, float]]:
    """
    Parse a piexif dict to get lat, long as floats
    Args:
        exif_dict:

    Returns:

    """
    position = None

    # noinspection PyBroadException
    try:
        position = (
            (1 if exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef] == b'N' else -1) *
            GPS.exif_rational_dms_to_float(exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]),
            (1 if exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] == b'E' else -1) *
            GPS.exif_rational_dms_to_float(exif_dict['GPS'][piexif.GPSIFD.GPSLongitude])
        )
    except Exception:
        pass

    return position


def get_piexif_dms_from_decimal(lat_lng) -> Dict:
    lat, lng = lat_lng
    gps_fields = {
        piexif.GPSIFD.GPSLatitudeRef: b'N' if lat > 0 else b'S',
        piexif.GPSIFD.GPSLongitudeRef: b'E' if lat > 0 else b'W',
        piexif.GPSIFD.GPSLatitude: GPS.degrees_float_to_dms_rational_string(abs(lat)),
        piexif.GPSIFD.GPSLongitude: GPS.degrees_float_to_dms_rational_string(abs(lng))
    }
    return gps_fields


def get_date_taken(exif_dict) -> Optional[datetime]:
    date = None
    date_taken = None
    tz_taken = None

    if piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
        date_taken = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]  # format b'2022:02:14 03:59:32'
    if piexif.ExifIFD.OffsetTimeOriginal in exif_dict['Exif']:
        tz_taken = exif_dict['Exif'][piexif.ExifIFD.OffsetTimeOriginal]  # format b'-05:00'

    if date_taken is not None:
        date_string = date_taken.decode('utf-8').replace(':', '-', 2)  # exif date separator is :
        if tz_taken is not None:
            date_string = date_string + ' ' + tz_taken.decode('utf-8')

        date = parse(date_string)

    return date
