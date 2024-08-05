from PIL import Image, ImageOps,ImageDraw, ImageFont
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from watermark import resize,io,log
from watermark import exif_extractor

logger = log.get_logger(__file__)


def get_max_font_size_by_date_and_loc(bar, draw, multiline_text, max_box_width_radio,max_box_height_radio, fontsize=-1):

    bar_image_w, bar_image_h = bar.size
    max_textbox_width = bar_image_w * max_box_width_radio
    max_textbox_height = bar_image_h * max_box_height_radio

    if fontsize ==-1:
        res = 10
        fnt = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", size=res)
        while 1:
            draw_box = draw.multiline_textbbox((0,0),multiline_text,font=fnt,spacing=max(10, int(bar_image_h*0.1)),font_size=res)
            box_w = draw_box[2] - draw_box[0]
            box_h = draw_box[3] - draw_box[1]
            if box_w>max_textbox_width or (box_h > max_textbox_height) :
                return box_w,box_h,res
            res+=1
            fnt = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", size=res)
    else:
        fnt = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", size=fontsize)
        draw_box = draw.multiline_textbbox((0,0),multiline_text,font=fnt,spacing=max(10, int(bar_image_h*0.1)),font_size=fontsize)
        box_w = draw_box[2] - draw_box[0]
        box_h = draw_box[3] - draw_box[1]
        return box_w,box_h,fontsize

def get_model_name(exif_info):
    if exif_info.get("Make","").lower() == "dji":
        return exif_info["Product Name"]
    return exif_info.get("Camera Model Name", None)


def get_maker_logo(exif_info):
    maker = exif_info.get("Make",None)
    if maker is not None:
        return io.get_svg_image_object(f"assets/logos/{maker.lower()}/1-{maker.lower()}.svg")
    return None

def get_datetime(exif_info):
    datetime = exif_info.get("Date/Time Original",None)
    return datetime

def get_gps(exif_info):
    la = exif_info.get("GPS Latitude",None)
    lo = exif_info.get("GPS Longitude",None)
    if la is not None and lo is not None and '0 deg' not in la and '0 deg' not in lo:
        return f"{la} {lo}"
    return None

def get_focal_info(exif_info):
    res = []
    # Exposure Time	F Number	ISO	Focal Length
    if "Focal Length" in exif_info:
        res.append(exif_info["Focal Length"])
    if "F Number" in exif_info:
        res.append(f'f{exif_info["F Number"]}')

    if "Exposure Time" in exif_info:
        res.append(f'{exif_info["Exposure Time"]}s')

    if "ISO" in exif_info:
        res.append(f'ISO {exif_info["ISO"]}')
    
    if len(res):
        return " ".join(res)
    return None


def make_bar(image, exif_info, content, font_size=-1):
    # print(image.size)
    # print(exif_info)
    w,h = image.size
    bar_image = Image.new("RGB",(w,int(h*0.07)),(256,256,256))
    bar_image_w, bar_image_h = bar_image.size

    logger.info(f"bar w = {bar_image_w}, bar_h = {bar_image_h}")

    draw = ImageDraw.Draw(bar_image)

    # draw text, half opacity
    # d.text((10, 10), exif_info["Date/Time Original"],fill=(0,0,0))
    # # draw text, full opacity
    # d.text((10, 60), exif_info["GPS Latitude"], fill=(0,0,0))

    top_margin = int(bar_image_h*0.05)
    left_margin = int(bar_image_w*0.02)

    # single_line_font_size = get_font_size(bar_image, draw)
    # print(single_line_font_size)
    datetime = get_datetime(exif_info)
    gps = get_gps(exif_info)
    
    if datetime is not None and gps is not None:
        max_box_height_radio = 0.8
        data_and_loc_draw_text = f'{datetime}\n{gps}'
    elif datetime is not None:
        max_box_height_radio = 0.2
        data_and_loc_draw_text = datetime
    elif gps is not None:
        max_box_height_radio = 0.2
        data_and_loc_draw_text = gps
    else:
        data_and_loc_draw_text = None
    fnt = None
    if data_and_loc_draw_text is not None:
        text_w, text_h, font_size = get_max_font_size_by_date_and_loc(bar_image, draw, data_and_loc_draw_text, 0.3, max_box_height_radio, fontsize=font_size)
        fnt = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", size=font_size)
        draw.multiline_text((left_margin, int((bar_image_h-text_h)/2) - int(min(20, bar_image_h*0.035))), data_and_loc_draw_text,font=fnt, fill=(0, 0, 0),spacing=max(10, int(bar_image_h*0.1)),font_size=font_size)

    model_name = get_model_name(exif_info)
    focal_info = get_focal_info(exif_info)

    model_name_and_focal_text = None
    if model_name is not None and focal_info is not None:
        model_name_and_focal_text = f"{model_name}\n{focal_info}"
    elif model_name is not None:
        model_name_and_focal_text = f"{model_name}"
    elif focal_info is not None:
        model_name_and_focal_text = f"{focal_info}"
    
    # print(model_name_and_focal_text)
    if model_name_and_focal_text is not None:
        # print(model_name_and_focal_text)
        text_w, text_h, font_size = get_max_font_size_by_date_and_loc(bar_image, draw, model_name_and_focal_text, 0.3, 0.8, font_size)
        draw.multiline_text((bar_image_w - left_margin - text_w, int((bar_image_h-text_h)/2) - int(min(20, bar_image_h*0.035))), model_name_and_focal_text, font=fnt,fill=(0, 0, 0),spacing=max(10, int(bar_image_h*0.1)),font_size=font_size)
        model_name_and_focal_wdith = text_w

    # print(content)
    if content is not None:
        text_w, text_h, font_size = get_max_font_size_by_date_and_loc(bar_image, draw, content, 0.3, 0.4, font_size)
        fnt = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", size=font_size)
        draw.multiline_text((int((bar_image_w  - text_w)/2), int((bar_image_h-text_h)/2)), content, font=fnt,fill=(0, 0, 0),spacing=max(10, int(bar_image_h*0.1)),font_size=font_size)
        
    logo_image = get_maker_logo(exif_info)
    if logo_image is not None and model_name_and_focal_text is not None:
        logo_image_w, logo_image_h = logo_image.size
        if exif_info.get("Make","").lower() in ["xiaomi","canon"]:
            logo_h = int(bar_image_h*0.15)
        else:
            logo_h = int(bar_image_h*0.4)
        logo_w = int(logo_image_w/logo_image_h*logo_h)
        logo_resize_image = logo_image.resize((logo_w, logo_h))

        bar_image.paste(logo_resize_image, (int(bar_image_w - left_margin - model_name_and_focal_wdith - int(left_margin/5) - logo_w), int((bar_image_h-logo_h)/2)))


    # bar_image.show()
    return bar_image, font_size


def get_image_with_bar(path, exif_info, content, font_size=-1):
    image = io.get_image_object(path)
    # exif_info = exif_extractor.extracte_exif_info(path)
    bar,res_font_size = make_bar(image, exif_info, content, font_size=font_size)
    dest_image = Image.new("RGB",(image.size[0], image.size[1]+bar.size[1]),(0,0,0))
    dest_image.paste(image, (0, 0))
    dest_image.paste(bar, (0, image.size[1]))
    final_image = resize.resize_image(dest_image)
    return final_image, font_size



if __name__ == "__main__":
    path = "data/2024-07-28打印/-1110493408950546188_IMG_0176.JPG"
    path = "data/2024-07-28打印/IMG_0778.HEIC"
    path = "data/2024-07-28打印/-1110493408950546188_IMG_0176.JPG"
    path = "data/2024-07-28打印/IMG_20220611_161933.jpg"
    final_image =get_image_with_bar(path, exif_extractor.extracte_exif_info(path),content="榆次·太原理工大学")

    final_image.show()