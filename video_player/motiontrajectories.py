import argparse
import cv2
import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from PIL import Image
from collections import defaultdict
from scipy.spatial import distance
from tqdm import tqdm

import constants
import operations
from traceplace import Traceplace


class MotionTrajectories:

    def __init__(self, markup_file, out_dir, human_number=None, marker_pos='lower_center'):
        self.__data = pd.read_csv(markup_file, names=['frame', 'id', 'bb_y', 'bb_x', 'bb_h', 'bb_w'])
        self.__human = human_number
        if self.__human is not None:
            self.__data = self.__data[self.__data['id'] == self.__human]
        self.__outdirectory = out_dir
        self.__background = np.asarray(Image.open(constants.BACKGROUND_READY_IMAGE))
        self.__markerpos = Traceplace[str(marker_pos).upper()]
        self.__distances = defaultdict(int)


    def calculateTraceStatistics(self):
        '''
        Calculate statistics about trajectories of movement
        '''
        print('Calculate statistics about movement...')
        self.__drawTrajectories()
        trajectories_imgnames = self.__saveResults()
        print('Success!')
        return trajectories_imgnames


    def __drawTrajectories(self):
        '''
        Visualize trajectories of movement and calculate their lengths
        '''
        prev_point = dict()
        for _, row in tqdm(self.__data.iterrows()):
            human_id = int(row['id'])
            color = operations.get_color(human_id)
            point = operations.get_point(row, self.__markerpos)
            if int(human_id) not in prev_point.keys():
                self.__background = cv2.circle(self.__background, point, radius=3, color=color, thickness=5)
                prev_point[human_id] = point
            else:
                self.__background = cv2.line(self.__background, point, prev_point[human_id], color=color, thickness=2)
                self.__distances[human_id] += distance.euclidean(point, prev_point[human_id])
                prev_point[human_id] = point


    def __drawBarChartDistances(self):
        '''
        Visualize lengths of trajectories as a bar chart
        '''
        if not os.path.exists(self.__outdirectory):
            os.makedirs(self.__outdirectory)
        fig, ax = plt.subplots(figsize=(12, 9))
        plt.rcParams.update({'font.size': 8})
        plt.subplots_adjust(left=0.03, bottom=0.03, right=0.97, top=0.97)
        plt.grid()
        d = self.__distances
        ax.barh(np.arange(len(d)), list(d.values()), zorder=2)
        ax.set_yticks(np.arange(len(d)))
        ax.set_yticklabels(list(map(str, d.keys())))
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_title('Covered distances by players')
        ax.set_xlabel('Pixels')
        fig.savefig(os.path.join(self.__outdirectory, 'covered_distances___{}.png'.format(self.__human)))
        return go.Bar(x=list(d.values()), y=list(map(str, d.keys())), orientation='h', name='',
                      marker={'color': 'royalblue'})


    def __saveResults(self):
        '''
        Save information about trajectories of movement in json-file or as an image
        '''
        if not os.path.exists(self.__outdirectory):
            os.makedirs(self.__outdirectory)
        if self.__human is None:
            Image.fromarray(self.__background).save(os.path.join(self.__outdirectory, 'trajectories.png'))
            plotly_object = self.__drawBarChartDistances()
            return plotly_object
        else:
            Image.fromarray(self.__background).save(os.path.join(self.__outdirectory,
                                                                 'trajectories___{}.png'.format(self.__human)))
            json_filename = 'covered_distance___human_{}.json'.format(self.__human)
            with open(os.path.join(self.__outdirectory, json_filename), 'w') as fp:
                json.dump(self.__distances, fp)
            return None


def init_argparse():
    '''
    Initializes argparse
    '''
    parser = argparse.ArgumentParser(
        description='Statistics about movement: build trajectories and calculate covered distances')
    parser.add_argument(
        '--markup',
        nargs='?',
        help='Markup file',
        required=True,
        type=str)
    parser.add_argument(
        '--out_dir',
        nargs='?',
        help='Output directory for saving files with calculated statistics',
        required=True,
        type=str)
    parser.add_argument(
        '--human',
        nargs='?',
        help='Number of sportsman',
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
    # Calculate statistics about trajectories
    mt = MotionTrajectories(markup_file=args.markup, out_dir=args.out_dir,
                            human_number=args.human, marker_pos=args.traceplace)
    mt.calculateTraceStatistics()


if __name__ == '__main__':
    main()