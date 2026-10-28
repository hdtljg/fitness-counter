import datetime
import math
from pathlib import Path

import cv2
import numpy as np
import tqdm
from mediapipe.python.solutions import drawing_utils as mp_drawing
from mediapipe.python.solutions import pose as mp_pose

import counter
import poseclassifier as pc
import poseembedding as pe
import resultsmooth as rs
import visualizer as vs
from exercises import get_exercise

BASE_DIR = Path(__file__).resolve().parent
POSE_SAMPLES_FOLDER = BASE_DIR / 'fitness_poses_csvs_out'
OUTPUT_DIR = BASE_DIR / 'video-output'


def video_process(video_path, flag, output_path=None, show=False):
    """Run pose classification and repetition counting on a video file.

    Args:
      video_path: input video path.
      flag: exercise number (1=pushup, 2=squat, 3=pullup).
      output_path: optional output video path. Defaults to ``video-output/``.
      show: whether to open an OpenCV preview window (needs a display).
    """
    exercise = get_exercise(flag)
    class_name = exercise['class_name']

    input_path = Path(video_path).expanduser()
    if not input_path.is_file():
        raise FileNotFoundError(f'视频不存在: {input_path}')

    if output_path is None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        output_path = OUTPUT_DIR / f"{exercise['output_prefix']}-sample-out-{timestamp}.mp4"
    else:
        output_path = Path(output_path).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)

    video_cap = cv2.VideoCapture(str(input_path))
    if not video_cap.isOpened():
        raise RuntimeError(f'无法打开视频: {input_path}')

    video_n_frames = video_cap.get(cv2.CAP_PROP_FRAME_COUNT)
    video_fps = video_cap.get(cv2.CAP_PROP_FPS)
    if not math.isfinite(video_fps) or video_fps <= 0:
        video_fps = 24.0
    video_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if video_width <= 0 or video_height <= 0:
        video_cap.release()
        raise RuntimeError(f'无法读取视频尺寸: {input_path}')

    pose_tracker = mp_pose.Pose()
    pose_embedder = pe.FullBodyPoseEmbedder()
    pose_classifier = pc.PoseClassifier(
        pose_samples_folder=POSE_SAMPLES_FOLDER,
        pose_embedder=pose_embedder,
        class_name=class_name,
        top_n_by_max_distance=30,
        top_n_by_mean_distance=10)
    pose_classification_filter = rs.EMADictSmoothing(window_size=10, alpha=0.2)
    repetition_counter = counter.RepetitionCounter(
        class_name=class_name,
        enter_threshold=6,
        exit_threshold=4)
    pose_classification_visualizer = vs.PoseClassificationVisualizer(
        class_name=class_name,
        plot_x_max=video_n_frames,
        plot_y_max=10)

    out_video = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*'mp4v'),
        video_fps,
        (video_width, video_height))
    if not out_video.isOpened():
        video_cap.release()
        pose_tracker.close()
        raise RuntimeError(f'无法创建输出视频: {output_path}')

    total_frames = int(video_n_frames) if video_n_frames > 0 else None
    try:
        with tqdm.tqdm(total=total_frames, position=0, leave=True) as pbar:
            while True:
                success, input_frame = video_cap.read()
                if not success:
                    break

                input_frame = cv2.cvtColor(input_frame, cv2.COLOR_BGR2RGB)
                result = pose_tracker.process(image=input_frame)
                pose_landmarks = result.pose_landmarks

                output_frame = input_frame.copy()
                if pose_landmarks is not None:
                    mp_drawing.draw_landmarks(
                        image=output_frame,
                        landmark_list=pose_landmarks,
                        connections=mp_pose.POSE_CONNECTIONS)

                if pose_landmarks is not None:
                    frame_height, frame_width = output_frame.shape[0], output_frame.shape[1]
                    landmarks = np.array(
                        [[lmk.x * frame_width, lmk.y * frame_height, lmk.z * frame_width]
                         for lmk in pose_landmarks.landmark],
                        dtype=np.float32)
                    assert landmarks.shape == (33, 3), \
                        f'Unexpected landmarks shape: {landmarks.shape}'

                    pose_classification = pose_classifier(landmarks)
                    pose_classification_filtered = pose_classification_filter(
                        pose_classification)
                    repetitions_count = repetition_counter(
                        pose_classification_filtered)
                else:
                    pose_classification = None
                    # Keep the EMA window advancing while no pose is detected.
                    pose_classification_filter(dict())
                    pose_classification_filtered = None
                    repetitions_count = repetition_counter.n_repeats

                output_frame = pose_classification_visualizer(
                    frame=output_frame,
                    pose_classification=pose_classification,
                    pose_classification_filtered=pose_classification_filtered,
                    repetitions_count=repetitions_count)

                frame_bgr = cv2.cvtColor(
                    np.asarray(output_frame), cv2.COLOR_RGB2BGR)
                out_video.write(frame_bgr)

                if show:
                    cv2.imshow('video', frame_bgr)
                    if cv2.waitKey(1) in [ord('q'), 27]:
                        break

                pbar.update()
    finally:
        out_video.release()
        video_cap.release()
        pose_tracker.close()
        if show:
            cv2.destroyAllWindows()

    print(f'视频处理结束，输出保存在 {output_path}')
    return str(output_path)
