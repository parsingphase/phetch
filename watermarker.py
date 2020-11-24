from typing import Tuple

from PIL import Image, ImageStat
from PIL.ImageFile import ImageFile


class Watermarker:
    short_edge_watermark_ratio: float
    watermark: ImageFile
    watermark_opacity: float
    watermark_brightness_threshold: int  # max target area brightness to use the "light" watermark

    def __init__(self, watermark_file: str) -> None:
        super().__init__()
        self.watermark = Image.open(watermark_file)
        self.inverse_watermark = self.invert_watermark(self.watermark)
        self.short_edge_watermark_ratio = 0.14  # default
        self.watermark_opacity = 0.5  # default
        self.watermark_brightness_threshold = 200  # default

    def __del__(self):
        self.watermark.close()

    def set_watermark_size(self, short_edge_ratio: float):
        self.short_edge_watermark_ratio = short_edge_ratio

    def set_watermark_opacity(self, opacity: float):
        self.watermark_opacity = opacity

    def mark_in_place(self, image_file_path: str) -> None:
        """
        Apply the loaded watermark to the specified image and save it

        :param image_file_path:
        :return:
        """
        image: ImageFile = Image.open(image_file_path)
        image_file = self.watermark_image(image)
        image_file.save(image_file_path)

    def watermark_image(self, image: ImageFile) -> ImageFile:
        """
        Add the watermark to the loaded image object

        :param image:
        :return:
        """
        watermark_width, watermark_height = self.calculate_watermark_dimensions(image)
        watermark_left = image.width - watermark_width
        watermark_top = image.height - watermark_height
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

    def calculate_watermark_dimensions(self, image_file: ImageFile) -> Tuple[int, int]:
        """
        Calculate the size a watermark should be for a given Image object such that the
        width of the watermark is self.short_edge_watermark_ratio of the larger image's longer dimension
        :param image_file:
        :return:
        """
        is_tall = image_file.height > image_file.width
        watermark_aspect = self.watermark.width / self.watermark.height
        if is_tall:
            watermark_width = int(image_file.height * self.short_edge_watermark_ratio)
        else:
            watermark_width = int(image_file.width * self.short_edge_watermark_ratio)
        watermark_height = int(watermark_width / watermark_aspect)
        return watermark_width, watermark_height

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
        r, g, b, a = local_watermark.split()
        a = a.point(lambda i: i * self.watermark_opacity)
        local_watermark = Image.merge('RGBA', (r, g, b, a))
        return local_watermark

    @staticmethod
    def invert_watermark(watermark: Image):
        r, g, b, a = watermark.split()
        r = r.point(lambda i: 255 - i)
        g = g.point(lambda i: 255 - i)
        b = b.point(lambda i: 255 - i)
        return Image.merge('RGBA', (r, g, b, a))
