import piexif
from .gps import GPS


def get_clean_lat_long_from_piexif(exif_dict):
    """
    Parse a piexif dict to get lat, long as floats
    Args:
        exif_dict:

    Returns:

    """
    position = None

    try:
        position = (
            (1 if exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef] == b'N' else -1) *
            GPS.exif_rational_dms_to_float(exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]),
            (1 if exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] == b'E' else -1) *
            GPS.exif_rational_dms_to_float(exif_dict['GPS'][piexif.GPSIFD.GPSLongitude])
        )
    except:
        pass

    return position
