from typing import Tuple

from PIL import Image
from PIL.ImageFile import ImageFile


class Watermarker:
    short_edge_watermark_ratio: float
    watermark: ImageFile
    watermark_opacity: float

    def __init__(self, watermark_file: str) -> None:
        super().__init__()
        self.watermark = Image.open(watermark_file)
        self.short_edge_watermark_ratio = 0.14  # default
        self.watermark_opacity = 0.5  # default

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
        watermark_position = (image.width - watermark_width, image.height - watermark_height)
        local_watermark = self.prepare_pastable_watermark(watermark_width, watermark_height)
        image = self.apply_prepared_watermark(image, local_watermark, watermark_position)
        return image

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
        short side of the watermark is self.short_edge_watermark_ratio of the larger image
        :param image_file:
        :return:
        """
        is_tall = image_file.height > image_file.width
        watermark_aspect = self.watermark.width / self.watermark.height
        if is_tall:
            watermark_width = int(image_file.width * self.short_edge_watermark_ratio)
            watermark_height = int(watermark_width / watermark_aspect)
        else:
            watermark_height = int(image_file.height * self.short_edge_watermark_ratio)
            watermark_width = int(watermark_height * watermark_aspect)
        return watermark_width, watermark_height

    def prepare_pastable_watermark(self, watermark_width: int, watermark_height: int) -> Image:
        """
        Scale and apply opacity to watermark as required for use at specified size
        :param watermark_width:
        :param watermark_height:
        :return:
        """
        local_watermark = self.watermark.resize((watermark_width, watermark_height))
        r, g, b, a = local_watermark.split()
        a = a.point(lambda i: i * self.watermark_opacity)
        local_watermark = Image.merge('RGBA', (r, g, b, a))
        return local_watermark
