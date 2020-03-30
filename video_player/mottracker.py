'''
Based on utils.datasets.py, utils.visualization.py, demo.py, track.py
from project Towards-Realtime-MOT (https://github.com/Zhongdao/Towards-Realtime-MOT)
'''

import os
import logging
import argparse
import cv2
import torch
import numpy as np

import constants
import operations
from videodataloader import VideoDataLoader

from utils.log import logger
from utils.timer import Timer
from tracker.multitracker import JDETracker


class MOTTracker:
    '''
    Shortened realization of Multi Object Tracker
    '''

    def __init__(self, input_video, gpu_number):
        '''
        Constructor
        :param input_video: video for tracking objects
        :param gpu_number: GPU number of videocard to launch algorithm of detection and tracking
        '''
        os.makedirs(constants.RESULTS_FOLDER, exist_ok=True)
        self.__video = input_video
        self.__gpu = gpu_number
        # Adjust names for saving information about tracking
        basename = os.path.splitext(os.path.basename(self.__video))[0]
        self.__markupfile = os.path.join(constants.RESULTS_FOLDER, str(basename)+'.txt')
        self.__markedvideo = os.path.join(constants.RESULTS_FOLDER, str(basename)+'.avi')
        # directory for saving marked frames of video with tracking objects
        self.__framedir = os.path.join(constants.RESULTS_FOLDER, str(basename))
        os.makedirs(self.__framedir, exist_ok=True)


    def __adjustTracker(self):
        '''
        Load video as a set of frames
        '''
        logger.setLevel(logging.INFO)
        logger.info('Loading video...')
        self.__dataloader = VideoDataLoader(self.__video, constants.OUTPUT_FRAME_SIZE)
        logger.info('Video was loaded!')
        self.__framerate = self.__dataloader.frame_rate
        logger.info('FPS: \t {}'.format(self.__framerate))
        logger.info('Frames: \t {}'.format(len(self.__dataloader)))


    def __makeMarkedVideo(self):
        '''
        Assemble marked frames with tracking objects into one video
        '''
        logger.info('Making tracking video...')
        cmd_str = 'ffmpeg -f image2 -i {}/%05d.jpg -c:v copy {}'.format(self.__framedir, self.__markedvideo)
        os.system(cmd_str)
        logger.info('Tracking video was made!')


    def __trackObjects(self):
        '''
        Implement tracking objects
        '''
        logger.info('Start tracking...')
        try:
            self.__evalSeq()
        except Exception as e:
            logger.info(e)
        logger.info('Tracking finished!')


    def trackVideo(self):
        '''
        Track humans on video:
        '''
        self.__adjustTracker()
        self.__trackObjects()
        self.__makeMarkedVideo()


    def __writeTrackingResults(self, results):
        '''
        Save results of tracked bboxes into file of markup
        :param results: list, which contains information about frames, detected humans and vertices of bounding boxes
        '''
        with open(self.__markupfile, 'w') as f:
            for frame_id, tlwhs, track_ids in results:
                for tlwh, track_id in zip(tlwhs, track_ids):
                    if track_id < 0:
                        continue
                    x1, y1, w, h = tlwh
                    x2, y2 = x1 + w, y1 + h
                    # frame_number, id_human, coordinates x, y of top left and bottom right corners of bbox
                    line = '{frame},{id},{x1},{y1},{w},{h}\n'.format(frame=frame_id, id=track_id,
                                                                     x1=x1, y1=y1, x2=x2, y2=y2, w=w, h=h)
                    f.write(line)
        logger.info('Results of tracking were saved to {}'.format(self.__markupfile))


    def __collectArgumentParserParams(self):
        '''
        Collect parameters for JDE Tracker as a collected argparse object
        :return: argparse object with parameters
        '''
        parser.add_argument('--cfg', type=str, default=constants.TRACKER_CONFIG)
        parser.add_argument('--weights', type=str, default=constants.TRACKER_WEIGHTS)
        parser.add_argument('--img-size', type=int, default=constants.OUTPUT_FRAME_SIZE)
        parser.add_argument('--iou-thres', type=float, default=constants.IOU_THRESHOLD)
        parser.add_argument('--conf-thres', type=float, default=constants.CONFIDENCE_THRESHOLD)
        parser.add_argument('--nms-thres', type=float, default=constants.SUPPRESSION_THRESHOLD)
        parser.add_argument('--track-buffer', type=int, default=constants.TRACKING_BUFFER)
        res = parser.parse_args()
        return res


    def __evalSeq(self):
        '''
        Track objects using JDE algorithm
        '''
        os.environ['CUDA_VISIBLE_DEVICES'] = str(self.__gpu)
        logger.info('GPU id: \t {}'.format(self.__gpu))
        argument_parser = self.__collectArgumentParserParams()
        tracker = JDETracker(argument_parser, frame_rate=self.__framerate)
        timer = Timer()
        results = []
        frame_id = 0
        for path, img, img0 in self.__dataloader:
            if frame_id % 20 == 0:
                logger.info('Processing frame {} ({:.2f} fps)'.format(frame_id, 1./max(1e-5, timer.average_time)))
            # Run tracking
            timer.tic()
            blob = torch.from_numpy(img).cuda().unsqueeze(0)
            online_targets = tracker.update(blob, img0)
            online_tlwhs, online_ids = [], []
            for t in online_targets:
                tlwh, tid = t.tlwh, t.track_id
                if (tlwh[2]*tlwh[3] > constants.MIN_BOX_AREA) and (tlwh[2] / tlwh[3] <= 1.6):
                    online_tlwhs.append(tlwh)
                    online_ids.append(tid)
            timer.toc()
            # Save results
            results.append((frame_id, online_tlwhs, online_ids))
            online_img = self.__plotTracking(img0, online_tlwhs, online_ids, frame_id=frame_id)
            cv2.imwrite(os.path.join(self.__framedir, '{:05d}.jpg'.format(frame_id)), online_img) # save marked frame
            frame_id += 1
        self.__writeTrackingResults(results)


    def __plotTracking(self, img, tlwhs, obj_ids, frame_id=0, ids2=None):
        '''
        Plot tracked bboxes for the frame of video
        :param img: frame of video
        :return: frame with tracked bounding boxes
        '''
        img = np.ascontiguousarray(np.copy(img))
        text_scale = max(1, img.shape[1]/1500.0)
        text_thickness = 1 if text_scale > 1.1 else 1
        line_thickness = max(1, int(img.shape[1]/500.0))
        # Draw information about the number of frame and an amount of detected humans
        cv2.putText(img, 'frame: {}   humans: {}'.format(frame_id, len(tlwhs)), (0, int(15*text_scale)),
                    cv2.FONT_HERSHEY_PLAIN, text_scale, color=(0, 0, 255), thickness=2)
        # Draw bboxes
        for i, tlwh in enumerate(tlwhs):
            x1, y1, w, h = tlwh
            bbox = tuple(map(int, (x1, y1, x1+w, y1+h)))
            obj_id = int(obj_ids[i])
            id_text = '{}'.format(int(obj_id))
            if ids2 is not None:
                id_text = id_text + ', {}'.format(int(ids2[i]))
            # Draw rectangle of bbox
            cv2.rectangle(img, bbox[0:2], bbox[2:4], color=operations.get_color(abs(obj_id)), thickness=line_thickness)
            # Draw id of detected human
            cv2.putText(img, id_text, (bbox[0], bbox[1]+30), cv2.FONT_HERSHEY_PLAIN, text_scale,
                        color=(0, 0, 255), thickness=text_thickness)
        return img


def init_argparse():
    '''
    Initialize argparse
    '''
    parser = argparse.ArgumentParser(description='Multiple Object Tracking')
    parser.add_argument(
        '--input_video',
        nargs='?',
        help='Video to track objects',
        required=True,
        type=str)
    parser.add_argument(
        '--gpu',
        nargs='?',
        help='Number of GPU to implement tracking',
        default=constants.GPU_NUMBER,
        type=int)
    return parser


if __name__ == '__main__':
    parser = init_argparse()
    # Extract arguments of script
    args = parser.parse_args()
    # Launch tracker
    jde = MOTTracker(args.input_video, args.gpu)
    jde.trackVideo()