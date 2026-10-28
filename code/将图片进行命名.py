import os
import shutil

def rename_images(folder_path, output_folder=None, prefix="image", start_index=1, suffix=""):
    """
    重命名指定文件夹中的所有图片文件。

    :param folder_path: 包含图片的文件夹路径
    :param output_folder: 重命名后的图片保存路径（可选）
    :param prefix: 文件名前缀
    :param start_index: 起始序号
    :param suffix: 文件名后缀（包括文件扩展名）
    """
    # 检查输入文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"Error: Folder {folder_path} does not exist.")
        return

    # 如果未指定输出文件夹，则使用输入文件夹
    if output_folder is None:
        output_folder = folder_path

    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 获取文件夹中的所有文件
    files = os.listdir(folder_path)

    # 筛选出图片文件（假设图片文件扩展名为 .jpg, .png, .jpeg）
    image_extensions = {'.jpg', '.png', '.jpeg'}
    images = [f for f in files if os.path.splitext(f)[1].lower() in image_extensions]

    # 按序号重命名图片
    for i, image in enumerate(images, start=start_index):
        # 构造新的文件名
        new_filename = f"{prefix}_{i:03d}{suffix}"
        new_filepath = os.path.join(output_folder, new_filename)

        # 构造原始文件路径
        original_filepath = os.path.join(folder_path, image)

        # 重命名文件C:\Users\gyg\Desktop\mediapipe-Fitness-counter-master\code\训练集\引体向上\下
        shutil.move(original_filepath, new_filepath)
        print(f"Renamed {original_filepath} to {new_filepath}")

if __name__ == '__main__':
    # 示例用法
    folder_path = input("请输入包含图片的文件夹路径：")
    output_folder = input("请输入输出文件夹路径（可选，直接回车跳过）：") or None
    prefix = input("请输入文件名前缀（默认为'image'）：") or "image"
    start_index = int(input("请输入起始序号（默认为1）：") or 1)
    suffix = input("请输入文件名后缀（包括文件扩展名，例如'.jpg'或'.png'）：") or ".jpg"

    rename_images(folder_path, output_folder, prefix, start_index, suffix)
