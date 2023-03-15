from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import argparse

def main(image_path):
    # 读取图片并转换为RGB数组
    img = Image.open(image_path)
    img = img.convert("RGB")
    img_data = np.array(img)

    # 对颜色进行聚类分析，选出最具代表性的5个颜色
    kmeans = KMeans(n_clusters=5).fit(img_data.reshape(-1, 3))
    colors = kmeans.cluster_centers_.astype(int)

    # 创建画布并绘制小方形
    color_squares = Image.new('RGB', (100, 20))
    for i in range(5):
        color_square = Image.new('RGB', (20, 20), tuple(colors[i]))
        color_squares.paste(color_square, (i * 20, 0))

    # 打印结果
    print("The 5 most representative colors in the image are:")
    for color in colors:
        print("#%02x%02x%02x" % tuple(color))

    # 显示画布并保存图片
    color_squares.show()
    color_squares.save("color_squares.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get the 5 most representative colors of an image.")
    parser.add_argument("image_path", type=str, help="the path of the image file")
    args = parser.parse_args()
    main(args.image_path)
