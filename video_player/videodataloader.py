'''
Based on utils.datasets.py from project Towards-Realtime-MOT (https://github.com/Zhongdao/Towards-Realtime-MOT)
'''

import numpy as np
import cv2

import constants


class VideoDataLoader:
    '''
    Implement class of loading video as a set of frames
    '''

    def __init__(self, path, img_size=(1088, 608)):
        '''
        Constructor
        :param path: video
        :param img_size: size of extracted frames
        '''
        self.cap = cv2.VideoCapture(path)
        self.frame_rate = int(round(self.cap.get(cv2.CAP_PROP_FPS)))
        self.count = 0
        self.w, self.h = self.__getFrameSize(int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                             int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                                             img_size[0], img_size[1])


    def __iter__(self):
        self.count = -1
        return self


    def __next__(self):
        self.count += 1
        if self.count >= len(self):
            raise StopIteration
        res, img0 = self.cap.read() # BGR format
        while img0 is None:
            print('Failed to load frame {:d}'.format(self.count))
            self.count += 1
            if self.count >= len(self):
                raise StopIteration
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.count)
            res, img0 = self.cap.read()  # BGR format
        img0 = cv2.resize(img0, (self.w, self.h), interpolation=cv2.INTER_AREA) # resize extracted frame
        # Padded resize
        img = self.__getPaddedRectangularFrame(img0)
        # Normalize RGB
        img = img[:, :, ::-1].transpose(2, 0, 1)
        img = np.ascontiguousarray(img, dtype=np.float32)
        img /= 255.0
        return self.count, img, img0


    def __len__(self):
        n_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))  # number of files
        return n_frames


    def __getFrameSize(self, vw, vh, dw, dh):
        wa, ha = float(dw)/vw, float(dh)/vh
        a = min(wa, ha)
        return int(vw*a), int(vh*a)


    def __getPaddedRectangularFrame(self, img):
        shape = img.shape[:2]  # shape = [height, width]
        width, height = constants.OUTPUT_FRAME_SIZE
        ratio = min(float(height)/shape[0], float(width)/shape[1])
        new_shape = (round(shape[1]*ratio), round(shape[0]*ratio))  # new_shape = [width, height]
        dw = (width-new_shape[0])/2  # width padding
        dh = (height-new_shape[1])/2  # height padding
        top, bottom = round(dh-0.1), round(dh+0.1) # top and bottom borders
        left, right = round(dw-0.1), round(dw+0.1) # left and right borders
        img = cv2.resize(img, new_shape, interpolation=cv2.INTER_AREA)  # resized image, no border
        # Padded rectangular image
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(127.5, 127.5, 127.5))
        return img