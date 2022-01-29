import piexif
from gps_tools.piexif_utils import get_clean_lat_long_from_piexif


def run_cli():
    exif_dict = piexif.load("tmp/Exports/2022-01-16/IMG_6105-DeNoiseAI-standard (Bald Eagle).jpg")
    print(get_clean_lat_long_from_piexif(exif_dict))


if __name__ == '__main__':
    run_cli()
