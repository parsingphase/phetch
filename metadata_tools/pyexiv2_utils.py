from typing import Dict, Set
from gps_tools.gps import GPS

EXIF_KEY_LATITUDE = 'Exif.GPSInfo.GPSLatitude'
EXIF_KEY_LONGITUDE = 'Exif.GPSInfo.GPSLongitude'

IPTC_KEY_SUBJECT = 'Iptc.Application2.ObjectName'
IPTC_KEY_KEYWORDS = 'Iptc.Application2.Keywords'

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


def round_gps_location(exif, gps_dp: int) -> Dict:
    """
    Take the GPS EXIF data (in pyexiv2 format) from the supplied image and rounds its lat/long to the specified number
     of decimal points
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
        revised_location[EXIF_KEY_LATITUDE] = GPS.round_dms_as_decimal(lat, gps_dp)

    if lon:
        revised_location[EXIF_KEY_LONGITUDE] = GPS.round_dms_as_decimal(lon, gps_dp)

    return revised_location


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


def extract_iptc_keywords(iptc: Dict) -> Set[str]:
    """
    Get keywords from IPTC data as a list
    :param iptc:
    :return:
    """
    keywords = []
    if IPTC_KEY_KEYWORDS in iptc:
        keywords = iptc[IPTC_KEY_KEYWORDS]
        if not isinstance(keywords, list):
            keywords = [keywords]

    return set(keywords)
