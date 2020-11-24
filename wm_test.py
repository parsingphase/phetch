from watermarker import Watermarker

w = Watermarker('watermark3.png')
w.mark_in_place('bee.jpg')
w.mark_in_place('squirrel.jpg')
