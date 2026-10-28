"""Extract every Nth frame from a video into JPEG files.

Example:
    python video_to_frames.py input.mp4 frames/ --interval 15
"""
import argparse
from pathlib import Path

import cv2


def video2frame(videos_path, frames_save_path, time_interval=15):
    if time_interval <= 0:
        raise ValueError('time_interval must be a positive integer')

    video = Path(videos_path)
    if not video.is_file():
        raise FileNotFoundError(f'Video does not exist: {video}')

    save_dir = Path(frames_save_path)
    save_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise RuntimeError(f'Cannot open video: {video}')

    count = 0
    saved = 0
    try:
        while True:
            success, image = cap.read()
            if not success:
                break
            count += 1
            if count % time_interval != 0:
                continue
            ok, buf = cv2.imencode('.jpg', image)
            if not ok:
                continue
            # tofile() handles non-ASCII paths on Windows better than imwrite().
            buf.tofile(str(save_dir / f'frame_{count:06d}.jpg'))
            saved += 1
    finally:
        cap.release()

    print(f'Read {count} frames, saved {saved} frames to {save_dir}')


def main():
    parser = argparse.ArgumentParser(
        description='Extract every Nth frame from a video.')
    parser.add_argument('video', help='input video path')
    parser.add_argument('output', help='output folder for JPEG frames')
    parser.add_argument('--interval', type=int, default=15,
                        help='save one frame every N frames (default: 15)')
    args = parser.parse_args()
    video2frame(args.video, args.output, args.interval)


if __name__ == '__main__':
    main()
