from datetime import datetime
from statistics import mode
from sys import argv
import os
import sys
from PIL import Image, ImageDraw, ImageFont
from image_tools import resize_image, add_canvas_to_image, read_image_metadata

LOGO_HEIGH = 70
TEXT_PADDING = 12
EXIF_INFO_SIZE = 26
COPYRIGHT_SIZE = 36
FONT_COLOR = (60, 60, 60)
FONT_COLOR_UNDER = (100, 100, 100)
EXIF_FONT = "Arial Bold.ttf"
EXIF_FONT_UNDER = "Arial.ttf"
COPYRIGHT_FONT = EXIF_FONT
TARGET_PATH = "/Users/Noah/Pictures/watermark/"
SHARING_PATH = "/Users/Noah/Pictures/分享输出/"

COPYRIGHT = f"©Noah {datetime.now().year}"
LOGO_MAPPING = {
        "NIKON CORPORATION": f"{sys.path[0]}/logo/nikon_logo.jpg",
             "FUJIFILM": f"{sys.path[0]}/logo/fuji_logo.jpg",
             "RICOH IMAGING COMPANY, LTD.": f"{sys.path[0]}/logo/ricoh_logo.jpg"
                }


def makeWatermark(imagePath):

    if not os.path.isdir(TARGET_PATH):
        os.makedirs(TARGET_PATH)

    fileName = os.path.basename(imagePath)
    target = f"{TARGET_PATH}{fileName}"

    img_meta_data = read_image_metadata(imagePath)
    print(img_meta_data)
    share_img_path = f"{SHARING_PATH}{fileName}"
    resize_image(imagePath, share_img_path, 3000)
    (canvas_img, resized_image) = add_canvas_to_image(share_img_path, 1.1)

    camera_make = img_meta_data['camera_make']
    camera_model = img_meta_data['camera_model']
    lens = img_meta_data['lens_info']
    if camera_model.upper() == lens.upper(): lens = ""
    camera_info = f"{camera_make} {camera_model} {lens} ".replace("NIKON CORPORATION NIKON", "NIKON").replace("Fujifilm Fujinon", "").replace("RICOH IMAGING COMPANY, LTD.", "").lstrip()
    shutting_params = f"{img_meta_data['focal_length']}mm F{img_meta_data['aperture']}  {img_meta_data['shutter_speed']}s  ISO{img_meta_data['iso']}"

    text_x = int((canvas_img.width - resized_image.width) // 2) 
    text_y = int(resized_image.height +  (canvas_img.height - resized_image.height) // 2) + 8

    font = ImageFont.truetype(font=EXIF_FONT, size=EXIF_INFO_SIZE)
    fontUnder = ImageFont.truetype(font=EXIF_FONT, size=EXIF_INFO_SIZE)
    font2 = ImageFont.truetype(font=COPYRIGHT_FONT, size=COPYRIGHT_SIZE)

    draw = ImageDraw.Draw(canvas_img)
    draw.text(xy=(text_x, text_y),
              text=camera_info, fill=FONT_COLOR, font=font)
    draw.text(xy=(text_x, text_y + EXIF_INFO_SIZE + 4),
              text=shutting_params, fill=FONT_COLOR_UNDER, font=fontUnder)

    textSize = draw.textsize(text=COPYRIGHT, font=font2)
    draw.text(xy=((text_x + resized_image.width) - textSize[0], text_y),
              text=COPYRIGHT, fill=FONT_COLOR, font=font2)
    
    make = img_meta_data['camera_make']
    logoPath = LOGO_MAPPING[make]
    logo = makeLogo(logoPath)
    if logo:
        x = (canvas_img.width - logo.width) // 2
        y = text_y
        canvas_img.paste(logo, (x, y - 8))

    canvas_img.save(target, quality=99, subsampling=0)

    print(f"{target} done")


def makeLogo(logo_path):

    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path)
        logoRadio = logo.width / logo.height
        return logo.resize((int(LOGO_HEIGH * logoRadio), LOGO_HEIGH))
    return None


def getImageFile(fileName):
    if fileName.lower().endswith('.jpg'):
        return [fileName]
    imageList = []
    for parent, _, filenames in os.walk(fileName):
        for name in filenames:
            if name.lower().endswith('.jpg'):
                imageList.append(os.path.join(parent, name))
    return imageList


if __name__ == '__main__':
    start = datetime.now()
    imagePaths = getImageFile(argv[1])
    for image in imagePaths:
        makeWatermark(image)
    end = datetime.now()
    print(end - start)
