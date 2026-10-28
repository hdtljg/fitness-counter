import datetime
import math
from pathlib import Path

import cv2
import numpy as np
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


def process(flag, output_path=None, show=True, camera_index=0):
    """Run pose classification and repetition counting on a webcam."""
    exercise = get_exercise(flag)
    class_name = exercise['class_name']

    if output_path is None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        output_path = OUTPUT_DIR / f"{exercise['output_prefix']}-camera-out-{timestamp}.mp4"
    else:
        output_path = Path(output_path).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)

    video_cap = cv2.VideoCapture(camera_index)
    if not video_cap.isOpened():
        raise RuntimeError(f'无法打开摄像头 {camera_index}')
    video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    camera_fps = video_cap.get(cv2.CAP_PROP_FPS)
    if not math.isfinite(camera_fps) or camera_fps <= 0 or camera_fps > 120:
        camera_fps = 24.0

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
        enter_threshold=5,
        exit_threshold=4)
    pose_classification_visualizer = vs.PoseClassificationVisualizer(
        class_name=class_name,
        plot_y_max=10)

    if show:
        cv2.namedWindow('video', cv2.WINDOW_NORMAL)

    out_video = None
    try:
        while video_cap.isOpened():
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

            # Create the writer lazily so the output resolution always matches
            # the resolution actually delivered by the camera.
            if out_video is None:
                frame_height, frame_width = frame_bgr.shape[:2]
                out_video = cv2.VideoWriter(
                    str(output_path),
                    cv2.VideoWriter_fourcc(*'mp4v'),
                    camera_fps,
                    (frame_width, frame_height))
                if not out_video.isOpened():
                    raise RuntimeError(f'无法创建输出视频: {output_path}')

            out_video.write(frame_bgr)

            if show:
                cv2.imshow('video', frame_bgr)
                if cv2.waitKey(1) in [ord('q'), 27]:
                    break
    finally:
        if out_video is not None:
            out_video.release()
        video_cap.release()
        pose_tracker.close()
        if show:
            cv2.destroyAllWindows()

    print(f'摄像头处理结束，输出保存在 {output_path}')
    return str(output_path)
