import piexif
from gps_tools.piexif_utils import getCleanLatLongFromPiExif


def run_cli():
    exif_dict = piexif.load("tmp/Exports/2022-01-16/IMG_6105-DeNoiseAI-standard (Bald Eagle).jpg")
    print(getCleanLatLongFromPiExif(exif_dict))


if __name__ == '__main__':
    run_cli()
