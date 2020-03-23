import argparse
import cv2
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from collections import defaultdict


def get_color(idx):
    idx = idx*3
    color = (np.asscalar(np.int16((37*idx) % 255)), np.asscalar(np.int16((17*idx) % 255)), np.asscalar(np.int16((29*idx) % 255)))
    return color


def init_argparse():
    '''
    Initializes argparse
    '''
    parser = argparse.ArgumentParser(description='Background extraction from the video')
    parser.add_argument(
        '--frames_folder',
        nargs='?',
        help='Folder with extracted frames',
        required=True,
        type=str)
    parser.add_argument(
        '--markup',
        nargs='?',
        help='Markup file',
        required=True,
        type=str)
    parser.add_argument(
        '--kernel_size',
        nargs='?',
        help='Number of frames to fill gaps in after the loss of detected objects',
        default=2,
        type=int)
    return parser


def is_bboxes_intersected(bbox1, bbox2):
    bbox_y1 = bbox1['bb_y']
    bbox_y2 = bbox1['bb_y'] + bbox1['bb_h']
    bbox_x1 = bbox1['bb_x']
    bbox_x2 = bbox1['bb_x'] + bbox1['bb_w']
    y1 = bbox2['bb_y'].values[0]
    y2 = bbox2['bb_y'].values[0] + bbox2['bb_h'].values[0]
    x1 = bbox2['bb_x'].values[0]
    x2 = bbox2['bb_x'].values[0] + bbox2['bb_w'].values[0]
    if (x1 > bbox_x1 and x1 < bbox_x2 and y1 > bbox_y1 and y1 < bbox_y2) or \
        (x2 > bbox_x1 and x2 < bbox_x2 and y2 > bbox_y1 and y2 < bbox_y2) or \
        (x1 > bbox_x1 and x1 < bbox_x2 and y2 > bbox_y1 and y2 < bbox_y2) or \
        (x2 > bbox_x1 and x2 < bbox_x2 and y1 > bbox_y1 and y1 < bbox_y2):
        return True
    return False


def main():
    parser = init_argparse()
    # Extract arguments of script
    args = parser.parse_args()
    df = pd.read_csv(args.markup, names=['frame', 'id', 'bb_y', 'bb_x', 'bb_h', 'bb_w'])
    n_files = len(os.listdir(args.frames_folder))
    last_appearance = defaultdict(int)
    for frame_id in tqdm(range(1, n_files)):
        ids = list(df[df['frame'] == frame_id]['id'].values)
        if frame_id > 1:
            for id in ids:
                if (frame_id - last_appearance[id] > 1) and (frame_id - last_appearance[id] < args.kernel_size):
                    bboxes = df[(df['frame'] == last_appearance[id]) & (df['id'] != id)][['id', 'bb_y', 'bb_x', 'bb_h', 'bb_w']]
                    prev_bb = df[(df['frame'] == last_appearance[id]) & (df['id'] == id)][['bb_y', 'bb_x', 'bb_h', 'bb_w']]
                    flag = False
                    for bb in bboxes.iterrows():
                        if flag:
                            break
                        flag = is_bboxes_intersected(bb[1], prev_bb)
                    if not flag:
                        cur_bb = df[(df['frame'] == frame_id) & (df['id'] == id)]
                        delta_y = cur_bb['bb_y'].values[0] - prev_bb['bb_y'].values[0]
                        delta_x = cur_bb['bb_x'].values[0] - prev_bb['bb_x'].values[0]
                        delta_h = cur_bb['bb_h'].values[0] - prev_bb['bb_h'].values[0]
                        delta_w = cur_bb['bb_w'].values[0] - prev_bb['bb_w'].values[0]
                        for i, fr in enumerate(range(last_appearance[id]+1, frame_id)):
                            new_y = prev_bb['bb_y'].values[0] + (i+1)*delta_y
                            new_x = prev_bb['bb_x'].values[0] + (i+1)*delta_x
                            new_h = prev_bb['bb_h'].values[0] + (i+1)*delta_h
                            new_w = prev_bb['bb_w'].values[0] + (i+1)*delta_w
                            im = cv2.imread(os.path.join(args.frames_folder, '{:05d}.jpg'.format(fr)))
                            intbox = tuple(map(int, (new_y, new_x, new_y + new_h, new_x + new_w)))
                            line_thickness = max(1, int(im.shape[1] / 500.))
                            text_scale = max(1, im.shape[1] / 1500.)
                            c = get_color(abs(id))
                            cv2.rectangle(im, intbox[0:2], intbox[2:4], color=c, thickness=line_thickness)
                            cv2.putText(im, str(id), (intbox[0], intbox[1] + 30), cv2.FONT_HERSHEY_PLAIN, text_scale,
                                        (0, 0, 255), 1)
                            cv2.imwrite(os.path.join(args.frames_folder, '{:05d}.jpg'.format(fr)), im)
                last_appearance[id] = frame_id
        else:
            for id in ids:
                last_appearance[id] = frame_id
    df.to_csv('1.txt', sep=',', index=False, header=False)


if __name__ == '__main__':
    main()