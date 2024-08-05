from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
import rawpy
import imageio
import math
import io
import glob
import pathlib
import sys
from collections import Counter
import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from watermark import log, io

register_heif_opener()

logger = log.get_logger(__file__)



def get_dest_size(w,h):
    # if isinstance(pad, int):
    #     h = h+pad
    # else:
    #     h = h*(1+pad)

    longer_edge = max(w, h)
    shoter_edge = min(w, h)
    if longer_edge/shoter_edge == 3/2:
        return w,h
    if longer_edge/shoter_edge > 3/2:
        # 根据长的算短的
        dest_long = longer_edge
        dest_short = longer_edge/3*2
        assert dest_short > shoter_edge
    else:
        dest_long = shoter_edge/2*3
        dest_short = shoter_edge
        assert dest_long > longer_edge

    if w > h:
        return math.ceil(dest_long), math.ceil(dest_short)
    return math.ceil(dest_short), math.ceil(dest_long)



def resize_image(image):
    w, h = image.size
    h_pad = h
    dest_w, dest_h = get_dest_size(w+20,h_pad+20)

    logger.info(f"w = {w}, h = {h}, dest_w = {dest_w}, dest_h = {dest_h}")

    paste_box = int((dest_w - w)/2), int((dest_h-h_pad)/2)

    
    new_image = Image.new("RGB",(dest_w,dest_h),(256,256,256))
    new_image.paste(image, paste_box)

    # image_shape = image.size()
    # new_image.show()
    return new_image

if __name__ == "__main__":
    # src = glob.glob("data/2024-07-28打印/*.*")
    # for fp in src:
    #     image = get_image_object(fp)
    #     resize_image(image)
    #     # image.show()
    path = "data/2024-07-28打印/IMG_0544.HEIC"
    resize_image(io.get_image_object(path))