import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from collections import defaultdict
from tqdm import tqdm

import operations


plt.rcParams.update({'font.size': 7})


class CombatsCounter():

    def __init__(self, markup_file, out_dir, human_number=None):
        self.__data = pd.read_csv(markup_file, names=['frame', 'id', 'bb_y', 'bb_x', 'bb_h', 'bb_w'])
        self.__ids = list(self.__data['id'].unique())
        self.__countframes = max(self.__data['frame'])
        self.__countsids = len(self.__ids)
        self.__outdirectory = out_dir
        self.__human = human_number
        self.__combatsmatrix = np.zeros((len(self.__ids), len(self.__ids)), dtype=np.int)


    def __buildCombatsMatrix(self):
        '''
        Build confusion matrix of combats between humans
        Element of confusion matrix [i, j] contains the number of combats between i and j objects
        '''
        existing_combats = defaultdict(set) # combats, which were registered on previous frame
        for frame_id in tqdm(range(1, self.__countframes+1)):
            # Extract all detected bbox on current frame
            frame_bboxes = self.__data[self.__data['frame'] == frame_id][['id', 'bb_y', 'bb_x', 'bb_h', 'bb_w']]
            n_bboxes = len(frame_bboxes)
            for i in range(n_bboxes-1):
                for j in range(i+1, n_bboxes):
                    id_i, id_j = int(frame_bboxes.iloc[i]['id']), int(frame_bboxes.iloc[j]['id'])
                    if id_i != id_j:
                        if operations.is_bbox_intersected(frame_bboxes.iloc[i], frame_bboxes.iloc[j]):
                            if id_j not in existing_combats[id_i]: # combat was not registered
                                # Add a combat to matrix on symmetric places
                                idx_i, idx_j = self.__ids.index(id_i), self.__ids.index(id_j)
                                self.__combatsmatrix[idx_i, idx_j] += 1
                                self.__combatsmatrix[idx_j, idx_i] += 1
                            # Register new combat
                            existing_combats[id_i].add(id_j)
                            existing_combats[id_j].add(id_i)
                        else:
                            # stop taking account completed combat
                            existing_combats[id_i].discard(id_j)
                            existing_combats[id_j].discard(id_i)


    def __buildHumanCombatsDictionary(self):
        '''
        Form the dictionary with combats for certain human
        key: value, where key - number of human, value - number of combats, which key-human has
        '''
        self.__combatsdict = dict()
        for i, comb in enumerate(list(self.__combatsmatrix[self.__ids.index(self.__human)])):
            if comb != 0:
                self.__combatsdict[self.__ids[i]] = self.__combatsmatrix[i, self.__ids.index(self.__human)]


    def __drawCombatsMatrix(self):
        '''
        Visualize confusion matrix of combats and save it as an image
        '''
        if not os.path.exists(self.__outdirectory):
            os.makedirs(self.__outdirectory)
        fig, ax = plt.subplots(figsize=(12, 9))
        plt.subplots_adjust(left=0.03, bottom=0.03, right=0.97, top=0.97)
        im = ax.imshow(self.__combatsmatrix)
        ax.set_xticks(np.arange(self.__countsids))
        ax.set_yticks(np.arange(self.__countsids))
        ax.set_xticklabels(self.__ids)
        ax.set_yticklabels(self.__ids)
        ax.tick_params(top=True, bottom=True, left=True, right=True, labeltop=True, labelright=True)
        colorbar = ax.figure.colorbar(im, ax=ax)
        colorbar.ax.set_ylabel('Number of combats', rotation=-90, va='bottom')
        for i in range(len(self.__ids)):
            for j in range(len(self.__ids)):
                ax.text(j, i, self.__combatsmatrix[i, j], ha='center', va='center', color='w')
        plt.savefig(os.path.join(self.__outdirectory, 'combats_matrix.png'))
        return go.Heatmap(z=self.__combatsmatrix, x=self.__ids, y=self.__ids, xgap=1, ygap=1, hoverongaps=False,
                          hovertemplate='i: %{x}<br>j: %{y}<br>combat: %{z}<br>', name='', colorscale='Viridis')


    def __drawBarChartHumanCombats(self):
        '''
        Visualize statistics about combats for certain human as a bar chart
        '''
        if not os.path.exists(self.__outdirectory):
            os.makedirs(self.__outdirectory)
        self.__buildHumanCombatsDictionary()
        d = self.__combatsdict
        if len(d) != 0:
            fig, ax = plt.subplots(figsize=(12, 9))
            plt.subplots_adjust(left=0.04, bottom=0.04, right=0.96, top=0.96)
            plt.grid()
            ax.bar(np.arange(len(d)), list(d.values()), zorder=2)
            ax.set_xticks(np.arange(len(d)))
            ax.set_xticklabels(list(map(str, d.keys())))
            ax.set_title('Covered distances by players')
            ax.set_ylabel('Pixels')
            fig.savefig(os.path.join(self.__outdirectory, 'combats___human_{}.png'.format(self.__human)))
            return go.Bar(x=np.arange(len(d)), y=list(d.values()), marker={'color': 'royalblue'})


    def calculateCombatsStatistics(self):
        '''
        Calculate statistics about combats and visualize it
        '''
        print('Calculate statistics about combats...')
        self.__buildCombatsMatrix()
        if self.__human is None:
            plotly_object = self.__drawCombatsMatrix()
        else:
            self.__buildHumanCombatsDictionary()
            plotly_object = self.__drawBarChartHumanCombats()
        print('Success!')
        return plotly_object


def init_argparse():
    '''
    Initializes argparse
    '''
    parser = argparse.ArgumentParser(description='Statistics about combats')
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
        default=None,
        type=int)
    return parser


def main():
    parser = init_argparse()
    # Extract arguments of script
    args = parser.parse_args()
    # Calculate statistics about combats
    comb_acc = CombatsCounter(args.markup, args.out_dir, args.human)
    comb_acc.calculateCombatsStatistics()


if __name__ == '__main__':
    main()