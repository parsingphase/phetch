import piexif
from gps_tools.gps import GPS
from typing import Optional, Tuple, Dict


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
