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

    def mark_in_place(self, dest_file_path: str) -> None:
        """
        Apply the loaded watermark to the specified image

        :param dest_file_path:
        :return:
        """
        dest_file: ImageFile = Image.open(dest_file_path)
        width = dest_file.width
        height = dest_file.height

        is_tall = height > width
        watermark_aspect = self.watermark.width / self.watermark.height
        if is_tall:
            watermark_width = int(width * self.short_edge_watermark_ratio)
            watermark_height = int(watermark_width / watermark_aspect)
        else:
            watermark_height = int(height * self.short_edge_watermark_ratio)
            watermark_width = int(watermark_height * watermark_aspect)

        position = (width - watermark_width, height - watermark_height)

        # print(self.short_edge_watermark_ratio)
        # print(watermark_width)
        # print(watermark_height)
        # print(position)

        local_watermark = self.prepare_pastable_watermark(watermark_width, watermark_height)

        transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        transparent.paste(dest_file, (0, 0))
        transparent.paste(local_watermark, position, local_watermark)

        out_file = transparent.convert('RGB')
        out_file.save('wm_' + dest_file_path)

    def prepare_pastable_watermark(self, watermark_width: int, watermark_height: int) -> Image:
        """
        Scale and apply opactiy to watermark as required for use at specified size
        :param watermark_width:
        :param watermark_height:
        :return:
        """
        local_watermark = self.watermark.resize((watermark_width, watermark_height))
        r, g, b, a = local_watermark.split()
        a = a.point(lambda i: i * self.watermark_opacity)
        local_watermark = Image.merge('RGBA', (r, g, b, a))
        return local_watermark
