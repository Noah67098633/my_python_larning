import os
from PIL import Image
import piexif
from fractions import Fraction
from datetime import datetime

def resize_image(input_path, output_path, max_size):
    with Image.open(input_path) as img:
        width, height = img.size
        if max(width, height) <= max_size:
            # 直接复制到新路径
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            os.system(f"cp {input_path} {output_path}")
            return

        # 缩放到指定大小
        if width > height:
            new_width = max_size
            new_height = int(height * new_width / width)
        else:
            new_height = max_size
            new_width = int(width * new_height / height)
        img = img.resize((new_width, new_height), resample=Image.LANCZOS)

        # 修改exif元数据
        exif = img.info.get("exif")
        if exif:
            exif_dict = piexif.load(exif)
            exif_dict["0th"][piexif.ImageIFD.XResolution] = (300, 1)
            exif_dict["0th"][piexif.ImageIFD.YResolution] = (300, 1)
            exif_dict["Exif"][piexif.ExifIFD.PixelXDimension] = new_width
            exif_dict["Exif"][piexif.ExifIFD.PixelYDimension] = new_height
            exif_bytes = piexif.dump(exif_dict)
        else:
            exif_bytes = None

        # 保留所有元数据
        metadata = img.info.copy()
        metadata["exif"] = exif_bytes
        img.save(output_path, "JPEG", **metadata, quality=99)
        print(f"image save to {output_path}")


def read_image_metadata(img_path):
    """
    Reads metadata from an image file.

    Args:
        img_path (str): Path to the image file.

    Returns:
        dict: A dictionary containing the extracted metadata.
    """

    # Create an empty dictionary to store the metadata
    metadata = {}

    try:
        # Read the EXIF data
        exif_data = piexif.load(img_path)

        # Extract the camera make and model
        camera_make = exif_data['0th'][piexif.ImageIFD.Make].decode('utf-8')
        camera_model = exif_data['0th'][piexif.ImageIFD.Model].decode('utf-8')
        metadata['camera_make'] = camera_make
        metadata['camera_model'] = camera_model

        # Extract the lens information
        try:
            lens_info = exif_data['Exif'][piexif.ExifIFD.LensModel].decode('utf-8')
        except KeyError:
            lens_info = "Unknown"
        metadata['lens_info'] = lens_info

        # Extract the aperture value
        aperture_value = exif_data['Exif'][piexif.ExifIFD.FNumber]
        aperture = aperture_to_string(aperture_value)
        
        metadata['aperture'] = aperture
        # Extract the shutter speed value
        shutter_speed_value = exif_data['Exif'][piexif.ExifIFD.ExposureTime]
        shutter_speed = str(Fraction(shutter_speed_value[0], shutter_speed_value[1]))
        metadata['shutter_speed'] = shutter_speed

        # Extract the ISO value
        iso_value = exif_data['Exif'][piexif.ExifIFD.ISOSpeedRatings]
        iso = str(iso_value)
        metadata['iso'] = iso

        # Extract the date/time value
        date_time_value = exif_data['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
        date_time = datetime.strptime(date_time_value, '%Y:%m:%d %H:%M:%S')
        metadata['date_time'] = date_time

        try:
            focal_length_value = exif_data['Exif'][piexif.ExifIFD.FocalLength]
            focal_length = str(focal_length_value[0] / focal_length_value[1])
            metadata['focal_length'] = focal_length
        except KeyError:
            metadata['focal_length'] = "Unknown"

    except Exception as e:
        # If an error occurs while reading the EXIF data, print an error message
        print(f"Error reading metadata: {e}")
        return None

    # Return the extracted metadata dictionary
    return metadata


def add_canvas_to_image(image_path, scale, max_long_edge = 3000):
    
    # 打开原始图片
    image = Image.open(image_path)
    isLandscape = image.width > image.height

    width, height = image.size
    radio = width / height
    new_width = int(width // scale)
    new_height = int(height // scale)
    
    if isLandscape:
        canvas_width = max_long_edge
        canvas_height = int(max_long_edge * (2 / 3))
        if canvas_height - new_height < canvas_width - new_width:
            new_height = int(canvas_height // scale)
            new_width = int(new_height * radio)

    else:
        canvas_height = max_long_edge
        canvas_width = int(max_long_edge * (2 / 3))
        if canvas_height - new_height > canvas_width - new_width:
            new_width = int(canvas_width // scale)
            new_height = int(new_width // radio)

    image = image.resize((new_width, new_height), resample=Image.LANCZOS)

    # 创建新的画布 
    canvas = Image.new('RGB', (canvas_width, canvas_height), color='white')

    # 计算图片在画布中的位置
    x = (canvas_width - new_width) // 2
    y = (canvas_height - new_height) // 2

    # 将原始图片粘贴到画布中心
    canvas.paste(image, (x, y))
    return (canvas, image)

# 光圈值转换函数
def aperture_to_string(value):
    # 将光圈值转换为浮点数
    f = float(Fraction(value[0], value[1]))
    return "{:.1f}".format(f)

