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
from watermark import log

register_heif_opener()

logger = log.get_logger(__file__)

def get_raw_image_object(image_path):
    with rawpy.imread(image_path) as raw:
        try:
            thumb = raw.extract_thumb()
        except rawpy.LibRawNoThumbnailError:
            logger.info(f"{image_path} no thumbnail found")
        except rawpy.LibRawUnsupportedThumbnailError:
            logger.info(f"{image_path} unsupported thumbnail")
        else:
            # if thumb.format == rawpy.ThumbFormat.JPEG:
            image = Image.open(io.BytesIO(thumb.data))
            image = ImageOps.exif_transpose(image)
            return image
        return Image()
    
def get_svg_image_object(image_path):
    drawing = svg2rlg(image_path)
    s = renderPM.drawToString(drawing, fmt="PNG")
    image = Image.open(io.BytesIO(s))
    return image


def get_image_object(image_path):
    path = pathlib.Path(image_path)
    if path.suffix.lower() in [".cr3"]:
        image = get_raw_image_object(image_path)
    else:
        image = Image.open(path)
        image = ImageOps.exif_transpose(image)
    return image