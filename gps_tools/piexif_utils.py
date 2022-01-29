import piexif
from .gps import GPS


def getCleanLatLongFromPiExif(exif_dict):
    """
    Parse a piexif dict to get lat, long as floats
    Args:
        exif_dict:

    Returns:

    """
    # print(exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef], exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef])
    return (
        (1 if exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef] == b'N' else -1) *
        GPS.exif_rational_dms_to_float(exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]),
        (1 if exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] == b'E' else -1) *
        GPS.exif_rational_dms_to_float(exif_dict['GPS'][piexif.GPSIFD.GPSLongitude])
    )
