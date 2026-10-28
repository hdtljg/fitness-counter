"""Rename all images in a folder to <prefix>_<index><ext>.

Example:
    python rename_images.py path/to/images --prefix image --start 1
"""
import argparse
import shutil
from pathlib import Path

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}


def rename_images(folder_path, output_folder=None, prefix='image',
                  start_index=1, suffix=None):
    """Rename images sequentially.

    Args:
      folder_path: folder containing the images.
      output_folder: destination folder; defaults to ``folder_path``.
      prefix: new file name prefix.
      start_index: first numeric index.
      suffix: force an extension (e.g. ``.jpg``); defaults to each file's
        original extension.
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        raise FileNotFoundError(f'Folder does not exist: {folder}')

    output = Path(output_folder) if output_folder else folder
    output.mkdir(parents=True, exist_ok=True)

    images = sorted(
        path for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )

    for index, image in enumerate(images, start=start_index):
        extension = suffix if suffix else image.suffix
        if extension and not extension.startswith('.'):
            extension = '.' + extension
        target = output / f'{prefix}_{index:03d}{extension}'
        if target.resolve() == image.resolve():
            print(f'Skipping {image} (already named correctly)')
            continue
        if target.exists():
            raise FileExistsError(f'Target already exists: {target}')
        shutil.move(str(image), str(target))
        print(f'Renamed {image} -> {target}')


def main():
    parser = argparse.ArgumentParser(
        description='Rename images in a folder sequentially.')
    parser.add_argument('folder', help='folder containing images')
    parser.add_argument('--output', '-o', default=None,
                        help='output folder (default: same folder)')
    parser.add_argument('--prefix', default='image', help='file name prefix')
    parser.add_argument('--start', type=int, default=1,
                        help='first numeric index (default: 1)')
    parser.add_argument('--suffix', default=None,
                        help="force extension, e.g. '.jpg'")
    args = parser.parse_args()
    rename_images(args.folder, args.output, args.prefix, args.start,
                  args.suffix)


if __name__ == '__main__':
    main()
