from datetime import datetime
from sys import argv
import os
from PIL import Image, ImageDraw, ImageFont
import piexif

BORDER = 60
LONGEDGE = 2000 - BORDER * 2
EXIFINFOSIZE = 20
COPYRIGHTSIZE = 40
TEXTINFOH = BORDER - (0.04 * BORDER)
EXIFFONT = "Arial"
COPYRIGHTFONT = "Arial"
TARGETPATH = "/Users/Noah/Pictures/watermark/"
COPYRIGHT = f"©Noah {datetime.now().year}"


def makeWatermark(imagePath):

    if not os.path.isdir(TARGETPATH):
        os.makedirs(TARGETPATH)

    fileName = os.path.basename(imagePath)
    target = f"{TARGETPATH}{fileName}"
    image = Image.open(imagePath)
    exifDic = piexif.load(image.info["exif"])
    

    (originw, originh) = image.size
    longEdge = 0
    shortEdge = 0
    islansacape = True
    if originw > originh:
        longEdge = originw
        shortEdge = originh
    else:
        longEdge = originh
        shortEdge = originw
        islansacape = False

    radio = float(LONGEDGE / longEdge)
    width = int(LONGEDGE if islansacape else shortEdge * radio)
    heigh = int(LONGEDGE if not islansacape else shortEdge * radio)
    image = image.resize((width, heigh), Image.LANCZOS)

    combineImage = Image.new(
        'RGB', (width + BORDER * 2, heigh + BORDER * 2), (255, 255, 255))
    combineImage.paste(image, (BORDER, BORDER))

    exifInfo = makeExifInfoText(imagePath)
    
    font = ImageFont.truetype(font=EXIFFONT, size=EXIFINFOSIZE)
    font2 = ImageFont.truetype(font=COPYRIGHTFONT, size=COPYRIGHTSIZE)

    draw = ImageDraw.Draw(combineImage)
    draw.text(xy=(BORDER, combineImage.height-TEXTINFOH),
              text=exifInfo, fill=(0, 0, 0), font=font)
    textSize = draw.textsize(text=COPYRIGHT, font=font2,)
    draw.text(xy=(combineImage.width - textSize[0] - BORDER, combineImage.height-TEXTINFOH),
              text=COPYRIGHT, fill=(0, 0, 0), font=font2)
    exifDic["Exif"][piexif.ExifIFD.PixelXDimension] = combineImage.width
    exifDic["Exif"][piexif.ExifIFD.PixelYDimension] = combineImage.height
    exifDic["thumbnail"] = None
    exifBytes = piexif.dump(exifDic)
    combineImage.save(target, quality=99, subsampling=0, exif=exifBytes)

    print(f"{imagePath} done")


def makeExifInfoText(imagePath):
    exifDic = piexif.load(imagePath)
    newDic = {}
    for ifd in ("0th", "Exif", "GPS", "1st"):
        for tag in exifDic[ifd]:
            newDic[piexif.TAGS[ifd][tag]["name"]] = exifDic[ifd][tag]

    model = str(newDic.get("Model", "-"), encoding="utf-8")
    make = str(newDic.get("Make", "-"), encoding="utf-8")
    lens = str(newDic.get("LensModel", "-"), encoding="utf-8")
    cameraInfo = f"{make} {model} {lens}"
    FStop = newDic.get("FNumber", "0")
    FStopNum = str(float(FStop[0]) / float(FStop[1]
                                       )).replace(".0", "") if len(FStop) == 2 else FStop[0]

    shutterTime = newDic.get("ExposureTime", "0")
    shutterTimeNum = f"{shutterTime[0]}/{shutterTime[1]}" if len(
        FStop) == 2 else "--/--"
    iso = newDic.get("ISOSpeedRatings", "-")
    param = f"F{FStopNum} {shutterTimeNum}s ISO{iso}"
    exifInfo = f"{cameraInfo} \n{param}"
    return exifInfo


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

