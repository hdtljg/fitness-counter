import cv2


def video2frame(videos_path, frames_save_path, time_interval):
    vidcap = cv2.VideoCapture(videos_path)
    success, image = vidcap.read()
    count = 0
    while success:
        success, image = vidcap.read()
        count += 1
        if count % time_interval == 0:
            cv2.imencode('.jpg', image)[1].tofile(frames_save_path + "/yt_%d.jpg" % count)
        # if count == 20:
        #   break
    print(count)


if __name__ == '__main__':
    videos_path = '1.mp4'

    frames_save_path = r'E:\mediapipe-Fitness-counter-1master\code\训练集\引体向上'
    time_interval = 15  # 隔一帧保存一次25
    video2frame(videos_path, frames_save_path, time_interval)
