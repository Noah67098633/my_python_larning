from datetime import datetime
from sys import argv
import os
import sys
from PIL import Image, ImageDraw, ImageFont
import piexif

BORDER = 140
LOGO_HEIGH = int(BORDER / 2)
CONTAINER_LONG_EDGE = 3000
CONTAINER_SHORT_EDGE = int(CONTAINER_LONG_EDGE * (2/3))
TEXT_PADDING = 12
EXIF_INFO_SIZE = 26
COPYRIGHT_SIZE = 36
FONT_COLOR = (60, 60, 60)
EXIF_FONT = "Arial Bold.ttf"
COPYRIGHT_FONT = EXIF_FONT
TARGET_PATH = "/Users/Noah/Pictures/watermark/"
COPYRIGHT = f"©Noah {datetime.now().year}"
LOGO_MAPPING = {"NIKON CORPORATION": f"{sys.path[0]}/logo/nikon_logo.jpg",
                "FUJIFILM": f"{sys.path[0]}/logo/fuji_logo.jpg"}


def makeWatermark(imagePath):

    if not os.path.isdir(TARGET_PATH):
        os.makedirs(TARGET_PATH)

    fileName = os.path.basename(imagePath)
    target = f"{TARGET_PATH}{fileName}"
    image = Image.open(imagePath)
    exifDic = piexif.load(image.info["exif"])

    (originw, originh) = image.size

    containerImageW = CONTAINER_LONG_EDGE if originw > originh else CONTAINER_SHORT_EDGE
    containerImageH = CONTAINER_LONG_EDGE if originw <= originh else CONTAINER_SHORT_EDGE
    radio = (containerImageW - BORDER * 2) / containerImageW if originw > originh else (
        containerImageH - BORDER * 2) / containerImageH
    scale = min((containerImageW * radio) / originw,
                (containerImageH * radio) / originh)

    image = image.resize(
        (int(originw * scale), int(originh * scale)), Image.LANCZOS)

    imageX = int((containerImageW - image.width) / 2)
    imageY = int((containerImageH - image.height) / 2)
    containerImage = Image.new(
        'RGB', (containerImageW, containerImageH), (255, 255, 255))

    # paper = Image.open(f"{os.getcwd()}/paper.jpg").resize((containerImageW, containerImageH), Image.LANCZOS)
    # containerImage.paste(paper, (0, 0))

    containerImage.paste(image, (imageX, imageY))

    exifInfo = makeExifInfoText(imagePath)

    font = ImageFont.truetype(font=EXIF_FONT, size=EXIF_INFO_SIZE)
    font2 = ImageFont.truetype(font=COPYRIGHT_FONT, size=COPYRIGHT_SIZE)

    textH = imageY + image.height + TEXT_PADDING
    draw = ImageDraw.Draw(containerImage)
    draw.text(xy=(imageX, textH),
              text=exifInfo, fill=FONT_COLOR, font=font)
    textSize = draw.textsize(text=COPYRIGHT, font=font2)
    draw.text(xy=((image.width + imageX) - textSize[0], textH),
              text=COPYRIGHT, fill=FONT_COLOR, font=font2)

    logo = makeLogo(exifDic)
    if logo:
        x = int((containerImage.width - logo.width) / 2)
        y = imageY + image.height
        containerImage.paste(logo, (x, y))

    exifDic["Exif"][piexif.ExifIFD.PixelXDimension] = containerImage.width
    exifDic["Exif"][piexif.ExifIFD.PixelYDimension] = containerImage.height
    exifDic["thumbnail"] = None
    exifBytes = piexif.dump(exifDic)

    containerImage.save(target, quality=99, subsampling=0, exif=exifBytes)

    print(f"{imagePath} done")


def makeExifInfoText(imagePath):
    exifDic = piexif.load(imagePath)
    for ifd in ("0th", "Exif", "GPS", "1st"):
        for tag in exifDic[ifd]:
            print(piexif.TAGS[ifd][tag]["name"], exifDic[ifd][tag])

    newDic = {}
    for ifd in ("0th", "Exif", "GPS", "1st"):
        for tag in exifDic[ifd]:
            newDic[piexif.TAGS[ifd][tag]["name"]] = exifDic[ifd][tag]

    model = str(newDic.get("Model", "-"), encoding="utf-8")
    make = str(newDic.get("Make", "-"), encoding="utf-8")
    lens =  str(newDic.get("LensModel", "-"), encoding="utf-8") if "LensMake" in newDic else ""
    if "x100" in model.lower():
        lens = ""
    cameraInfo = f"{make} {model} {lens}".replace(
        "NIKON CORPORATION NIKON", "NIKON").replace("Fujifilm Fujinon", "")
    FStop = newDic.get("FNumber", "-")
    FStopNum = str(float(FStop[0]) / float(FStop[1]
                                           )).replace(".0", "") if len(FStop) == 2 else FStop[0]
    FStopNum = FStopNum if ("LensMake" in newDic or "x100" in model.lower()) else "-"
    (mol, den) = newDic.get("ExposureTime", "0")
    shutterTimeNum = f"1/{round(den / mol, 1)}" if den is not 1 else f"{mol}"
    shutterTimeNum = shutterTimeNum.replace(".0", "")
    iso = newDic.get("ISOSpeedRatings", "-")
    param = f"F{FStopNum}  {shutterTimeNum}s  ISO{iso}"
    exifInfo = f"{cameraInfo} \n{param}"
    return exifInfo


def makeLogo(exifDic):
    make = str(exifDic["0th"][piexif.ImageIFD.Make], encoding="utf-8")
    logoPath = LOGO_MAPPING[make]

    if logoPath and os.path.exists(logoPath):
        logo = Image.open(logoPath)
        logoRadio = logo.width / logo.height
        # draw = ImageDraw.Draw(logo)
        # draw.rectangle((0,0,logo.width,logo.height), outline="red", width=4)
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
