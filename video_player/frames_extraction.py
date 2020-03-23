import argparse
import os
import cv2


FRAME_SIZE = (810, 608)


def init_argparse():
    '''
    Initializes argparse
    '''
    parser = argparse.ArgumentParser(description='Frames extraction from the video')
    parser.add_argument(
        '--input_video',
        nargs='?',
        help='Video for frames extraction',
        required=True,
        type=str)
    parser.add_argument(
        '--output_directory',
        nargs='?',
        help='Output directory to save extracted frames',
        required=True,
        type=str)
    return parser


def extract_frames(input_video, output_directory):
    '''
    Extract frames from input video and save them
    :param input_video: video for frames extraction
    :param output_directory: directory for saving extracted frames
    '''
    cap = cv2.VideoCapture(input_video)
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_id = 1
    if not os.path.exists(output_directory): # check the existance of output directory
        os.makedirs(output_directory)
    # Extract frames
    while frame_id <= n_frames:
        res, img0 = cap.read()
        if img0 is not None:
            img0 = cv2.resize(img0, FRAME_SIZE, interpolation = cv2.INTER_AREA)
            cv2.imwrite(os.path.join(output_directory, '{:05d}.jpg'.format(frame_id)), img0)
            if frame_id % 20 == 0:
                print('{} frames'.format(frame_id))
        else:
            print('Failed to extract frame {}'.format(frame_id))
        frame_id += 1


def main():
    parser = init_argparse()
    # Extract arguments of script
    args = parser.parse_args()
    # Extract frames from video and save them
    print('Start extracting frames...')
    extract_frames(args.input_video, args.output_directory)
    print('Frames extrtaction finished!')


if __name__ == '__main__':
    main()