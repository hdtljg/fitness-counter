import argparse

import trainingsetprocess as tp
import videocapture as vc
import videoprocess as vp
from exercises import EXERCISES, exercise_names, flag_from_name


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description='MediaPipe 健身动作计数（俯卧撑 / 深蹲 / 引体向上）')
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--video', metavar='PATH', help='输入视频路径')
    source.add_argument('--camera', action='store_true', help='调用摄像头实时检测')
    parser.add_argument(
        '--exercise', '-e', metavar='NAME',
        help='运动类型：' + ' / '.join(exercise_names()))
    parser.add_argument('--output', '-o', metavar='PATH', help='输出视频路径')
    parser.add_argument(
        '--show', action='store_true',
        help='处理视频时显示预览窗口（Docker 或无显示器环境不要加）')
    parser.add_argument(
        '--camera-index', type=int, default=0, help='摄像头编号，默认 0')
    return parser.parse_args(argv)


def _ask_exercise():
    raw = input("请输入检测的运动类型（数字）：1. 俯卧撑\t2. 深蹲\t3. 引体向上\n").strip()
    try:
        flag = int(raw)
    except ValueError:
        print('输入错误，请重新输入！')
        return None
    if flag not in EXERCISES:
        print('输入错误，请重新输入！')
        return None
    return flag


def interactive():
    """Original menu-driven workflow, kept for local users."""
    while True:
        menu = input(
            "请输入检测模式（数字）：1. 从本地导入视频检测\t2. 调用摄像头检测\t3. 退出\n"
        ).strip()
        if menu == '3':
            return
        if menu not in ('1', '2'):
            print('输入错误，请重新输入！')
            continue

        flag = _ask_exercise()
        if flag is None:
            continue

        try:
            tp.trainset_process(flag)
        except Exception as exc:  # noqa: BLE001 - print a friendly CLI message
            print(f'训练集准备失败：{exc}')
            continue

        if menu == '1':
            video_path = input(
                "请输入视频路径（例如：C:/Users/you/Desktop/squat.mp4）：").strip()
            if not video_path:
                print('输入的视频路径不能为空，请重新输入！')
                continue
            try:
                vp.video_process(video_path, flag)
            except Exception as exc:  # noqa: BLE001
                print(f'视频处理失败：{exc}')
        else:
            print('\n按英文状态下的 q 或 esc 退出摄像头采集')
            try:
                vc.process(flag)
            except Exception as exc:  # noqa: BLE001
                print(f'摄像头处理失败：{exc}')


def main(argv=None):
    args = parse_args(argv)
    if not args.video and not args.camera:
        interactive()
        return

    if not args.exercise:
        raise SystemExit(
            '使用 --video/--camera 时必须指定 --exercise，例如 --exercise squat')

    try:
        flag = flag_from_name(args.exercise)
    except ValueError as exc:
        raise SystemExit(str(exc))

    try:
        tp.trainset_process(flag)
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f'训练集准备失败：{exc}')

    if args.video:
        try:
            vp.video_process(args.video, flag, output_path=args.output, show=args.show)
        except Exception as exc:  # noqa: BLE001
            raise SystemExit(f'视频处理失败：{exc}')
    else:
        try:
            vc.process(
                flag,
                output_path=args.output,
                show=True,
                camera_index=args.camera_index)
        except Exception as exc:  # noqa: BLE001
            raise SystemExit(f'摄像头处理失败：{exc}')


if __name__ == '__main__':
    main()
