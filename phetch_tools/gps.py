from typing import Dict, Tuple, cast

Rational = Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]
EXIF_KEY_LATITUDE = 'Exif.GPSInfo.GPSLatitude'
EXIF_KEY_LONGITUDE = 'Exif.GPSInfo.GPSLongitude'
GPS_LOCATION_KEYWORD = 'Approximate GPS location'


class GPS:
    @staticmethod
    def string_to_exif_rational(text: str) -> Rational:
        """
        Given a Rational exif string, eg 71/1 81159000/10000000 0/1, unpack to (2-3) Tuple of (nom,denom)

        :param text:
        :return:
        """
        parts = text.split(' ')
        # cast = 'Trust me on the length!'
        tuples = cast(Rational, tuple(tuple(int(n) for n in p.split('/')) for p in parts))
        return tuples

    @staticmethod
    def exif_rational_dms_to_float(dms: Rational) -> float:
        """
        Given a Rational of Degrees, Minutes, Seconds, convert it to a float
        :param dms:
        :return:
        """
        float_parts = [v[0] / v[1] for v in dms]
        float_out = sum([float_parts[i] / pow(60, i) for i in range(0, len(float_parts))])
        return float_out

    @staticmethod
    def degrees_float_to_dms_rational_string(degrees: float):
        """
        Convert a float value to an EXIF degrees, minutes, seconds rational string

        :param degrees:
        :return:
        """
        minutes_dp = 6
        (int_degrees, frac_degrees) = [int(p) for p in str(degrees).split('.')]
        minutes = round(float(f'0.{frac_degrees}') * 60, minutes_dp)
        denominator = pow(10, minutes_dp)
        numerator = int(minutes * denominator)
        return f'{int_degrees}/1 {numerator}/{denominator} 0/1'

    @staticmethod
    def round_gps_location(exif, gps_dp: int) -> Dict:
        """
        Take the GPS EXIF data from the supplied image and rounds its lat/long to the specified number of decimal points
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

    @staticmethod
    def round_dms_as_decimal(dms: str, gps_dp: int) -> str:
        """
        Take an EXIF Rational DMS string, round it as a float of degrees, and re-encode it
        :param dms:
        :param gps_dp:
        :return:
        """
        old_lat = GPS.exif_rational_dms_to_float(GPS.string_to_exif_rational(dms))
        new_lat = round(old_lat, gps_dp)
        new_lat_string = GPS.degrees_float_to_dms_rational_string(new_lat)
        return new_lat_string
