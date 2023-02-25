import argparse
from PIL import Image

def resize_image(input_path, output_path, long_edge=3000):
    """
    将指定图片进行缩放，使其长边为指定长度，短边按比例缩放
    :param input_path: 输入图片路径
    :param output_path: 输出图片路径
    :param long_edge: 缩放后图片的长边长度，默认为3000
    """
    # 打开图片并获取长短边
    image = Image.open(input_path)
    width, height = image.size
    long_edge_org = max(width, height)
    short_edge_org = min(width, height)

    # 计算画布尺寸
    canvas_long_edge = int(long_edge_org * 1.1)  # 长边比图片长边多20%
    canvas_short_edge = int(canvas_long_edge * 2 / 3)  # 长边和短边比例为3:2

    # 创建画布
    if width > height:
        canvas_size = (canvas_long_edge, canvas_short_edge)
    else:
        canvas_size = (canvas_short_edge, canvas_long_edge)
    canvas = Image.new("RGB", canvas_size, (255, 255, 255))

    # 将图片粘贴进画布中间
    if width > height:
        offset = ((canvas_long_edge - width) // 2, (canvas_short_edge - height) // 2)
    else:
        offset = ((canvas_short_edge - width) // 2, (canvas_long_edge - height) // 2)
    canvas.paste(image, offset)

    # 缩放画布
    if width > height:
        canvas = canvas.resize((long_edge, int(long_edge * short_edge_org / long_edge_org)), Image.LANCZOS)
    else:
        canvas = canvas.resize((int(long_edge * short_edge_org / long_edge_org), long_edge), Image.LANCZOS)

    # 导出图片
    canvas.save(output_path, quality=99)  # 最高质量JPEG格式

if __name__ == '__main__':
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="将指定图片进行缩放")
    parser.add_argument("input", type=str, help="输入图片路径")
    parser.add_argument("output", type=str, help="输出图片路径")
    parser.add_argument("--long_edge", type=int, default=3000, help="缩放后图片的长边长度")
    args = parser.parse_args()

    # 调用函数进行图片缩放
    resize_image(args.input, args.output, args.long_edge)
