from pathlib import Path

import extracttrainingsetkeypoints as ek
import poseclassifier as pc
import poseembedding as pe
from exercises import get_exercise

BASE_DIR = Path(__file__).resolve().parent
CSV_DIR = BASE_DIR / 'fitness_poses_csvs_out'
IMAGES_IN_DIR = BASE_DIR / 'fitness_poses_images_in'
IMAGES_OUT_DIR = BASE_DIR / 'fitness_poses_images_out'


def _required_csvs(exercise):
    prefix = exercise['csv_prefix']
    return CSV_DIR / f'{prefix}_up.csv', CSV_DIR / f'{prefix}_down.csv'


def trainset_process(flag):
    """Ensure the CSV training set for the selected exercise exists.

    If both CSVs are present, nothing is rebuilt. Otherwise the program expects
    ``fitness_poses_images_in/<prefix>_up|down/*.jpg`` and bootstraps the CSVs.

    The images-in folder only needs the two classes of the selected exercise;
    other exercise folders in the same directory are ignored.
    """
    exercise = get_exercise(flag)
    csv_up, csv_down = _required_csvs(exercise)
    if csv_up.is_file() and csv_down.is_file():
        return

    class_names = [
        f"{exercise['csv_prefix']}_up",
        f"{exercise['csv_prefix']}_down",
    ]
    missing_dirs = [
        str(IMAGES_IN_DIR / name) for name in class_names
        if not (IMAGES_IN_DIR / name).is_dir()
    ]
    if missing_dirs:
        raise FileNotFoundError(
            '缺少训练图片目录：\n  ' + '\n  '.join(missing_dirs) +
            f'\n请按 README 的数据集格式准备图片，或保留 {CSV_DIR} 中已有的 CSV 文件。')

    bootstrap_helper = ek.BootstrapHelper(
        images_in_folder=str(IMAGES_IN_DIR),
        images_out_folder=str(IMAGES_OUT_DIR),
        csvs_out_folder=str(CSV_DIR),
        pose_class_names=class_names,
    )

    bootstrap_helper.print_images_in_statistics()
    bootstrap_helper.bootstrap(per_pose_class_limit=None)
    bootstrap_helper.print_images_out_statistics()
    bootstrap_helper.align_images_and_csvs(print_removed_items=False)
    bootstrap_helper.print_images_out_statistics()

    pose_embedder = pe.FullBodyPoseEmbedder()
    pose_classifier = pc.PoseClassifier(
        pose_samples_folder=str(CSV_DIR),
        pose_embedder=pose_embedder,
        class_name=exercise['class_name'],
        top_n_by_max_distance=30,
        top_n_by_mean_distance=10,
    )

    outliers = pose_classifier.find_pose_sample_outliers()
    print('Number of outliers: ', len(outliers))
    bootstrap_helper.analyze_outliers(outliers)
    bootstrap_helper.remove_outliers(outliers)
    bootstrap_helper.align_images_and_csvs(print_removed_items=False)
    bootstrap_helper.print_images_out_statistics()
