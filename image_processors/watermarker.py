"""
Class file for Watermarker
"""
from typing import Optional, Tuple

from iptcinfo3 import IPTCInfo
from PIL import Image, ImageStat
from PIL.ImageFile import ImageFile

from metadata_tools.iptc_utils import remove_iptcinfo_backup


def standard_save(image: Image, image_file_path: str):
    """
    PIL throws a lot of data away on save by default. Preserve it instead!

    :param image:
    :param image_file_path:
    :return:
    """
    image.save(
        image_file_path,
        quality=95,
        icc_profile=image.info['icc_profile'] if 'icc_profile' in image.info else None,
        exif=image.info["exif"],
        subsampling='4:4:4'
    )


def write_iptc(image_file_path: str, source_iptc: IPTCInfo):
    """
    Write iptc data to file (bit of a hack if we use iptcinfo3 but pyexiv2 is increasingly a trash-fire to install)

    :param image_file_path:
    :param source_iptc:
    :return:
    """
    dest_iptc = IPTCInfo(image_file_path, force=True)
    iptc_keys = [
        'supplemental category',
        'keywords',
        'contact',
        'date created',
        'digital creation date',
        'time created',
        'digital creation time',
        'by-line',
        'object name'
    ]
    for key in iptc_keys:
        source = source_iptc[key]
        if source:
            dest_iptc[key] = source

    dest_iptc.save()  # causes filename~ to be created!
    remove_iptcinfo_backup(image_file_path)


def read_iptc(image_file_path: str) -> IPTCInfo:
    """
    Read iptc data from file

    :param image_file_path:
    :return:
    """
    return IPTCInfo(image_file_path)


class Watermarker:
    """
    Tool to add transparent watermark to images
    """
    long_edge_watermark_ratio: float
    watermark: Image
    watermark_opacity: float
    watermark_brightness_threshold: int  # max target area brightness to use the "light" watermark

    def __init__(self, watermark_file: str) -> None:
        super().__init__()
        self.watermark = Image.open(watermark_file)
        self.inverse_watermark = self.invert_watermark(self.watermark)
        self.long_edge_watermark_ratio = 0.14  # default
        self.long_edge_border_ratio = 0.01  # default
        self.watermark_opacity = 0.5  # default
        self.watermark_brightness_threshold = 180  # default

    def __del__(self):
        self.watermark.close()

    def set_watermark_size(self, long_edge_ratio: float):
        """
        Set watermark width as proportion of image long edge
        :param long_edge_ratio:
        :return:
        """
        self.long_edge_watermark_ratio = long_edge_ratio

    def set_border_size(self, border_ratio: float):
        """
        Set watermark border offset as proportion of image long edge
        :param border_ratio:
        :return:
        """
        self.long_edge_border_ratio = border_ratio

    def set_watermark_opacity(self, opacity: float):
        """
        Set watermark opacity (0-1)
        :param opacity:
        :return:
        """
        self.watermark_opacity = float(opacity)

    def mark_in_place(self, image_file_path: str) -> None:
        """
        Apply the loaded watermark to the specified image and save it

        :param image_file_path:
        :return:
        """
        image: ImageFile = Image.open(image_file_path)
        iptc = read_iptc(image_file_path)
        image = self.watermark_image(image)
        standard_save(image, image_file_path)
        write_iptc(image_file_path, iptc)

    def copy_with_watermark(self, input_file: str, output_file: str, max_edge: Optional[int] = None) -> None:
        """
        Apply the loaded watermark to the specified image and save it

        :param max_edge:
        :param output_file:
        :param input_file:
        :return:
        """
        image: Image = Image.open(input_file)
        iptc = read_iptc(input_file)
        if max_edge is not None:
            if image.width > image.height:
                ratio = max_edge / image.width
                size = (max_edge, round(image.height * ratio))
            else:
                ratio = max_edge / image.height
                size = (round(image.width * ratio), max_edge)
            image = image.resize(size, Image.LANCZOS)

        image = self.watermark_image(image)
        standard_save(image, output_file)
        write_iptc(output_file, iptc)

    def watermark_image(self, image: ImageFile) -> ImageFile:
        """
        Add the watermark to the loaded image object

        :param image:
        :return:
        """
        watermark_width, watermark_height, border_w, border_h = self.calculate_watermark_dimensions(image)
        watermark_left = image.width - watermark_width - border_w
        watermark_top = image.height - watermark_height - border_h
        # "bright" area is approximate; we currently just go from top-left of watermark to bottom-right of image
        area_is_bright = self.watermark_area_is_bright(image, watermark_left, watermark_top)

        local_watermark = self.prepare_pastable_watermark(watermark_width, watermark_height, dark=area_is_bright)
        image = self.apply_prepared_watermark(image, local_watermark, (watermark_left, watermark_top))
        return image

    def watermark_area_is_bright(self, image: Image, watermark_left: int, watermark_top: int) -> bool:
        """
        Check if the mean brightness (crudely calculated) of the bottom-right corner is "bright" or "dark"
        :param image:
        :param watermark_left:
        :param watermark_top:
        :return:
        """
        target_area = image.crop((watermark_left, watermark_top, image.width - 1, image.height - 1))
        area_props = ImageStat.Stat(target_area)
        brightness = sum(area_props.mean) / len(area_props.mean)
        area_is_bright = brightness > self.watermark_brightness_threshold
        return area_is_bright

    @staticmethod
    def apply_prepared_watermark(image, local_watermark, watermark_position) -> ImageFile:
        """
        Apply a prepared watermark to an Image
        :param image:
        :param local_watermark:
        :param watermark_position:
        :return:
        """
        image = image.convert('RGBA')  # must convert to RGBA to merge with watermark
        image.paste(local_watermark, watermark_position, local_watermark)
        image = image.convert('RGB')  # must convert back to RGB to save jpg
        return image

    def calculate_watermark_dimensions(self, image_file: ImageFile) -> Tuple[int, int, int, int]:
        """
        Calculate the size a watermark should be for a given Image object such that the
        width of the watermark is self.short_edge_watermark_ratio of the larger image's longer dimension
        :param image_file:
        :return: watermark width, watermark height, border width, border height
        """
        is_tall = image_file.height > image_file.width
        watermark_aspect = self.watermark.width / self.watermark.height
        if is_tall:
            watermark_width = int(image_file.height * self.long_edge_watermark_ratio)
            border = int(image_file.height * self.long_edge_border_ratio)
        else:
            watermark_width = int(image_file.width * self.long_edge_watermark_ratio)
            border = int(image_file.width * self.long_edge_border_ratio)
        watermark_height = int(watermark_width / watermark_aspect)
        return watermark_width, watermark_height, border, border

    def prepare_pastable_watermark(self, watermark_width: int, watermark_height: int, dark: bool = False) -> Image:
        """
        Scale and apply opacity to watermark as required for use at specified size
        :param dark:
        :param watermark_width:
        :param watermark_height:
        :return:
        """
        watermark = self.inverse_watermark if dark else self.watermark
        local_watermark = watermark.resize((watermark_width, watermark_height))
        ch_r, ch_g, ch_b, ch_a = local_watermark.split()
        ch_a = ch_a.point(lambda i: i * self.watermark_opacity)
        local_watermark = Image.merge('RGBA', (ch_r, ch_g, ch_b, ch_a))
        return local_watermark

    @staticmethod
    def invert_watermark(watermark: Image):
        """
        Invert the watermark's RGB values pixel-by-pixel,
        ie make a dark watermark out of a light one
        :param watermark:
        :return:
        """
        ch_r, ch_g, ch_b, ch_a = watermark.split()
        ch_r = ch_r.point(lambda i: 255 - i)
        ch_g = ch_g.point(lambda i: 255 - i)
        ch_b = ch_b.point(lambda i: 255 - i)
        return Image.merge('RGBA', (ch_r, ch_g, ch_b, ch_a))
