from PIL import Image
import sys

def copy_image(image_path, scale):
    # 打开原始图片
    image = Image.open(image_path)

    # 获取原始图片的宽度和高度
    width, height = image.size

    # 计算新的宽度和高度
    new_width, new_height = int(width * scale), int(height * scale)

    # 创建新的画布
    canvas = Image.new('RGB', (new_width, new_height), color='white')

    # 计算图片在画布中的位置
    x = (new_width - width) // 2
    y = (new_height - height) // 2

    # 将原始图片粘贴到画布中心
    canvas.paste(image, (x, y))

    # 展示新的图片
    canvas.show()

if __name__ == '__main__':
    # 获取命令行参数
    image_path = sys.argv[1]
    scale = float(sys.argv[2])

    # 复制图片到画布
    copy_image(image_path, scale)
