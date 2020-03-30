import argparse
import sys
import cv2
import os
import numpy as np
from tqdm import tqdm

import constants


def init_argparse():
    '''
    Initialize argparse
    '''
    parser = argparse.ArgumentParser(description='Background extraction from the video')
    parser.add_argument(
        '--video',
        nargs='?',
        help='Path to the video',
        required=True,
        type=str)
    parser.add_argument(
        '--strategy',
        nargs='?',
        help='Choose the strategy of extracting the background from the video {}'.format(constants.BACKGROUND_STRATEGIES),
        default='median',
        type=str)
    parser.add_argument(
        '--frequency',
        nargs='?',
        help='''Number of frames which took part in the background extraction
        For median or mean strategy - amount of randomly uniform taken frames to get the 'MEDIAN' or 'MEAN' frame
        For cumulated strategy - 1/frequency is a value of accumulating the weights of frames
        ''',
        default=100,
        type=int)
    return parser


def get_cumulated_background(cap, total_frames, freq):
    '''
    Get matrix of background extracted from the video using cumulated weights of all frames
    :param cap: captured video
    :param total_frames: total number of frames in the video
    :param freq: frequency of cumulating the weights of previous frames
    :return: cumulated background matrix
    '''
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # set the position of video into its start
    # Set first frame as the base of result
    res = None
    _, frame = cap.read() # extract the first frame from the video
    cumulated_frame = np.float32(frame)
    # Cumulate next frames into result
    for fid in tqdm(range(1, int(total_frames))):
        cap.set(cv2.CAP_PROP_POS_FRAMES, fid)
        _, frame = cap.read()
        if frame is not None:
            cv2.accumulateWeighted(frame, cumulated_frame, freq)
            res = cv2.convertScaleAbs(cumulated_frame)
    return res


def get_calculated_background(cap, total_frames, freq, strategy):
    '''
    Get matrix of background calculated by the use of sum of random frames in the video
    :param cap: captured video
    :param total_frames: total number of frames in the video
    :param freq: count of frames choosen randomly
    :param strategy: strategy of calculating the matrix of background
    :return: background matrix
    '''
    # Get indices of randomly chosen frames which will be used for background extraction
    frame_indices = total_frames*np.random.uniform(size=freq) # random uniform rule
    # Collect the frames
    collected_frames = [] # storage of frames
    for _, fid in tqdm(enumerate(frame_indices)):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(fid))
        _ , frame = cap.read()
        collected_frames.append(frame)
    if collected_frames:
        # Calculate the background image according to chosen strategy
        if strategy == 'median':
            res = np.median(collected_frames, axis=0).astype(dtype=np.uint8)
        else:
            res = np.mean(collected_frames, axis=0).astype(dtype=np.uint8)
    else:
        res = None
    return res


def main():
    parser = init_argparse()
    # Extract arguments of script
    args = parser.parse_args()
    # Extract video and count of frames
    cap = cv2.VideoCapture(args.video)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    print('Amount of frames:\t{}'.format(total_frames))
    # Extract strategy
    strategy = args.strategy
    # Validate strategy
    if strategy not in constants.BACKGROUND_STRATEGIES:
        print('Not available strategy! Please choose the right one:\t{}'.format(constants.BACKGROUND_STRATEGIES))
        sys.exit(1)
    print('Strategy of background extraction:\t{}'.format(strategy))
    # Calculate and validate frequency
    if args.frequency <= 0:
        print('Not available value of frequency! Please choose the positive value...')
        sys.exit(1)
    if strategy == 'cumulated':
        freq = 1.0/args.frequency
    else:
        freq = min(args.frequency, total_frames)
    print('Frequency of frames:\t{}'.format(freq))
    # Extract the background from the video
    print('Background image extracting...')
    if strategy == 'cumulated':
        bg = get_cumulated_background(cap, total_frames, freq)
    else:
        bg = get_calculated_background(cap, total_frames, freq, strategy)
    # Save extracted background
    img_name = os.path.splitext(os.path.basename(args.video))[0]
    if bg is None:
        print('Background image was not extracted!')
    else:
        cv2.imwrite(img_name+'.png', bg)
        print('Background image was successfully extracted!')


if __name__ == '__main__':
    main()