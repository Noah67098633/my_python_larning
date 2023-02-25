import piexif
from fractions import Fraction
from datetime import datetime

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

    # Load the image
    img = open(img_path, 'rb')

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
        aperture = str(Fraction(aperture_value[0], aperture_value[1]))
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

    except Exception as e:
        # If an error occurs while reading the EXIF data, print an error message
        print(f"Error reading metadata: {e}")
        return None

    # Return the extracted metadata dictionary
    return metadata
