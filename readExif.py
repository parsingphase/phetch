import piexif
from metadata_tools.piexif_utils import get_decimal_lat_long_from_piexif


def run_cli() -> None:
    exif_dict = piexif.load("tmp/Exports/2022-01-16/IMG_6105-DeNoiseAI-standard (Bald Eagle).jpg")  # type: ignore
    print(get_decimal_lat_long_from_piexif(exif_dict))


if __name__ == '__main__':
    run_cli()
