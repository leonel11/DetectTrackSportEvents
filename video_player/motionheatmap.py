import argparse
import os
import pandas as pd
from PIL import Image

import constants
import operations
from heatmapper import Heatmapper
from traceplace import Traceplace


class MotionHeatmap():
    '''
    Implement class of building heamap of motion for detected and tracked players
    '''

    def __init__(self, markup_file, out_dir, human_number=None, marker_pos='lower_center'):
        '''
        Constructor
        :param markup_file: file with saved information about bboxes, ids of humans on each frame of video
        :param out_dir: directory for saving results
        :param human_number: id of human to count combats with other players (None - count combats for each player)
        :param marker_pos: marker of location of key points on bboxes to build a heatmap
        '''
        self.__data = pd.read_csv(markup_file, names=['frame', 'id', 'bb_y', 'bb_x', 'bb_h', 'bb_w'])
        self.__outdirectory = out_dir
        self.__background = Image.open(constants.BACKGROUND_READY_IMAGE)
        self.__human = human_number
        self.__markerpos = Traceplace[str(marker_pos).upper()]


    def __loadPoints(self):
        '''
        Load vertices of bounding boxes around objects
        '''
        if self.__human is not None:
            self.__points = [operations.get_point(row, self.__markerpos)
                             for _, row in self.__data[self.__data['id'] == self.__human].iterrows()]
        else:
            self.__points = [operations.get_point(row, self.__markerpos) for _, row in self.__data.iterrows()]


    def buildHeatmap(self):
        '''
        Build a heatmap of motion using coordinates of vertices of bounding boxes
        :return: heatmap of motion as an image
        '''
        print('Building the heatmap of motion...')
        self.__loadPoints()
        heatmapper = Heatmapper()
        heatmap_img = heatmapper.buildHeatmapOnImage(self.__points, self.__background)
        if heatmap_img is not None:
            if not os.path.exists(self.__outdirectory):
                os.makedirs(self.__outdirectory)
            # Save a heatmap as an image
            if self.__human is not None:
                heatmap_imgname = os.path.join(self.__outdirectory, 'heatmap___human_{}.png'.format(self.__human))
            else:
                heatmap_imgname = os.path.join(self.__outdirectory, 'heatmap.png')
            heatmap_img.save(heatmap_imgname)
            print('Success!')
        else:
            heatmap_img = self.__background
            print('Fail... Heatmap was not built!')
        return heatmap_img


def init_argparse():
    '''
    Initialize argparse
    '''
    parser = argparse.ArgumentParser(description='Build heatmap of movement')
    parser.add_argument(
        '--markup',
        nargs='?',
        help='Markup file',
        required=True,
        type=str)
    parser.add_argument(
        '--outfile',
        nargs='?',
        help='Output file to save heatmap',
        required=True,
        type=str)
    parser.add_argument(
        '--human',
        nargs='?',
        help='Number of sportsman',
        default=None,
        type=int)
    parser.add_argument(
        '--traceplace',
        nargs='?',
        help='Place of marker on the bbox where the trace is drawing',
        default='lower_center',
        type=str)
    return parser


def main():
    parser = init_argparse()
    # Extract arguments of script
    args = parser.parse_args()
    # Building a heatmap of motion
    mh = MotionHeatmap(markup_file=args.markup, out_file=args.out_dir, human_number=args.human,
                       marker_pos=args.traceplace)
    mh.buildHeatmap()


if __name__ == '__main__':
    main()