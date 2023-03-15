from datetime import datetime
from statistics import mode
from typing import List, Tuple
from sys import argv
import os
import sys
from PIL import Image, ImageDraw, ImageFont
from image_tools import resize_image, add_canvas_to_image, read_image_metadata


SHARED_PATH = "/Users/Noah/Pictures/分享输出/"
TARGET_PATH = "/Users/Noah/Pictures/watermark/"
COPYRIGHT_FONT_PATH = "Arial Bold.ttf"
EXIF_FONT_PATH = "Arial.ttf"

COPYRIGHT = "©Noah {}"
LOGO_HEIGH = 70


def make_watermark(image_path: str) -> None:
    """
    为指定图片加上水印，并保存到指定目录下。

    Args:
        image_path: 原始图片的路径
    Return:
        None
    """
    if not os.path.isdir(TARGET_PATH):
        os.makedirs(TARGET_PATH)

    # 读取图片元数据
    meta_data = read_image_metadata(image_path)

    # 生成输出文件名
    file_name = os.path.basename(image_path)
    target_file_path = os.path.join(TARGET_PATH, file_name)
    
    # 调整图片大小
    share_img_path = os.path.join(SHARED_PATH, file_name)
    resize_image(image_path, share_img_path, 3000)
    (canvas_img, resized_image) = add_canvas_to_image(share_img_path, 1.1)
    
    # 生成水印文字
    camera_brand = meta_data['camera_make']
    camera_model = meta_data['camera_model']
    lens_info = meta_data['lens_info']
    if camera_brand == lens_info:
        lens_info = ""
    camera_info = f"{camera_brand} {camera_model} {lens_info}".replace(
        "NIKON CORPORATION NIKON", "NIKON").replace(
        "Fujifilm Fujinon", "").replace(
        "RICOH IMAGING COMPANY, LTD.", "").lstrip()
    shutter_params = f"{meta_data['focal_length']}mm F{meta_data['aperture']}  {meta_data['shutter_speed']}/s  ISO{meta_data['iso']}"
    
    # 插入水印文字
    top_offset = int(resized_image.height + (canvas_img.height - resized_image.height) // 2)
    (text_x, text_y) = (int((canvas_img.width - resized_image.width) // 2), top_offset + 8)
    (font_size, font_color) = (26, (60, 60, 60))
    (under_font_size, under_font_color) = (26, (100, 100, 100))
    
    font = ImageFont.truetype(font=EXIF_FONT_PATH, size=font_size)
    font_under = ImageFont.truetype(font=EXIF_FONT_PATH, size=under_font_size)
    text_draw = ImageDraw.Draw(canvas_img)
    text_draw.text(xy=(text_x, text_y), text=camera_info, fill=font_color, font=font)
    text_draw.text(xy=(text_x, text_y + font_size + 4), text=shutter_params, fill=under_font_color, font=font_under)
    
    # 插入版权信息
    copyright_text = COPYRIGHT.format(datetime.now().year)
    copyright_font_size = 36
    copyright_font = ImageFont.truetype(font=COPYRIGHT_FONT_PATH, size=copyright_font_size)
    textSize = text_draw.textsize(text=copyright_text, font=copyright_font)
    text_draw.text(xy=((text_x + canvas_img.width // 1.1) - textSize[0], text_y),
              text=copyright_text, fill=font_color, font=copyright_font)
    # 插入品牌 Logo
    logo_path = CAMERA_BRAND_LOGO.get(camera_brand, None)
    logo = make_logo(logo_path, LOGO_HEIGH)
    if logo:
        x = (canvas_img.width - logo.width) // 2
        y = text_y
        canvas_img.paste(logo, (x, y))

    canvas_img.save(target_file_path, quality=99, subsampling=0)
    print(f"{target_file_path} done")


def make_logo(logo_path: str, logo_height: int) -> Image:
    """
    从指定路径读取品牌 Logo 并返回处理后的图像对象。

    Args:
        logo_path: Logo 文件的路径
        logo_height: Logo 图像压缩后的高度
    Return:
        处理后的图片对象
    """
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path)
        logo_ratio = logo.width / logo.height
        return logo.resize((int(logo_height * logo_ratio), logo_height))
    return None


def get_image_file(image_dir: str) -> List[str]:
    """
    获取指定目录中所有后缀名为 '.jpg' 的文件路径列表。

    Args:
        image_dir: 图片所在的目录
    Return:
        所有后缀名为 '.jpg' 的文件路径列表
    """
    image_paths = []
    for parent_dir, _, filenames in os.walk(image_dir):
        for file_name in filenames:
            if file_name.lower().endswith('.jpg'):
                image_paths.append(os.path.join(parent_dir, file_name))
    return image_paths


if __name__ == '__main__':
    start_time = datetime.now()
    image_paths = get_image_file(argv[1])
    for image_path in image_paths:
        make_watermark(image_path)
    end_time = datetime.now()
    print(f"Time cost is {end_time - start_time}.")
