from datetime import datetime
from sys import argv
import os
from PIL import Image, ImageDraw, ImageFont
import piexif

BORDER = 240
OUTPUTWIDTH = 3000
TEXTPADDING = 20
EXIFINFOSIZE = 40
COPYRIGHTSIZE = 60
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
    imageX = 0
    imageY = 0
    imageWidth = 0
    imageHeigh = 0
    if originw > originh:
        radio = originh / originw
        imageWidth = int(OUTPUTWIDTH - BORDER * 2)
        imageHeigh = int(imageWidth * radio)
        imageX = BORDER
        imageY = int((OUTPUTWIDTH - imageHeigh)  / 2)
    
    else:
        radio = originw / originh
        imageHeigh = int(OUTPUTWIDTH - BORDER * 2)
        imageWidth = int(imageHeigh * radio)
        imageY = BORDER
        imageX = int((OUTPUTWIDTH - imageWidth)  / 2)



    image = image.resize((imageWidth, imageHeigh), Image.LANCZOS)

    combineImage = Image.new(
        'RGB', (OUTPUTWIDTH, OUTPUTWIDTH), (255, 255, 255))
    combineImage.paste(image, (imageX, imageY))

    exifInfo = makeExifInfoText(imagePath)
    
    font = ImageFont.truetype(font=EXIFFONT, size=EXIFINFOSIZE)
    font2 = ImageFont.truetype(font=COPYRIGHTFONT, size=COPYRIGHTSIZE)

    textH = imageY + imageHeigh + TEXTPADDING
    draw = ImageDraw.Draw(combineImage)
    draw.text(xy=(imageX, textH),
              text=exifInfo, fill=(0, 0, 0), font=font)
    textSize = draw.textsize(text=COPYRIGHT, font=font2,)
    draw.text(xy=((imageWidth + imageX) - textSize[0], textH),
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

