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
    '''
    Implement class to count combats between detected and tracked players
    '''

    def __init__(self, markup_file, out_dir, human_number=None):
        '''
        Constructor
        :param markup_file: file with saved information about bboxes, ids of humans on each frame of video
        :param out_dir: directory for saving results
        :param human_number: id of human to count combats with other players (None - count combats for each player)
        '''
        self.__data = pd.read_csv(markup_file, names=['frame', 'id', 'bb_y', 'bb_x', 'bb_h', 'bb_w'])
        self.__ids = list(self.__data['id'].unique())
        self.__countframes = max(self.__data['frame'])
        self.__countsids = len(self.__ids)
        self.__outdirectory = out_dir
        self.__human = human_number


    def __buildCombatsMatrix(self):
        '''
        Build confusion matrix of combats between humans
        Element of confusion matrix [i, j] contains the number of combats between i and j humans
        '''
        existing_combats = defaultdict(set) # combats, which were registered on previous frame
        for frame_id in tqdm(range(1, self.__countframes+1)):
            # Extract all detected bboxes on current frame
            frame_bboxes = self.__data[self.__data['frame'] == frame_id][['id', 'bb_y', 'bb_x', 'bb_h', 'bb_w']]
            n_bboxes = len(frame_bboxes) # count of detected bboxes
            for i in range(n_bboxes-1):
                for j in range(i+1, n_bboxes):
                    id_i, id_j = int(frame_bboxes.iloc[i]['id']), int(frame_bboxes.iloc[j]['id'])
                    if id_i != id_j:
                        # Check if combat exists on current frame for i and j humans
                        if operations.is_bbox_intersected(frame_bboxes.iloc[i], frame_bboxes.iloc[j]):
                            if id_j not in existing_combats[id_i]: # combat was not registered earlier
                                # Add a combat to matrix on symmetric places
                                idx_i, idx_j = self.__ids.index(id_i), self.__ids.index(id_j)
                                self.__combatsmatrix[idx_i, idx_j] += 1
                                self.__combatsmatrix[idx_j, idx_i] += 1
                            # Register what new combat between i and j humans start taking place since current frame
                            existing_combats[id_i].add(id_j)
                            existing_combats[id_j].add(id_i)
                        else:
                            # stop taking account combat between i and j humans if it takes place
                            existing_combats[id_i].discard(id_j)
                            existing_combats[id_j].discard(id_i)


    def __buildHumanCombatsDictionary(self):
        '''
        Form the dictionary with combats for certain human (parameter of class)
        {key: value, ...}, where key - id of human, value - number of combats, which certain human has
        '''
        self.__combatsdict = dict()
        if self.__human in self.__ids: # check if id human was found out
            for i, comb in enumerate(list(self.__combatsmatrix[self.__ids.index(self.__human)])):
                if comb != 0:
                    self.__combatsdict[self.__ids[i]] = self.__combatsmatrix[i, self.__ids.index(self.__human)]


    def __drawCombatsMatrix(self):
        '''
        Visualize confusion matrix of combats as a heatmap
        '''
        if not os.path.exists(self.__outdirectory):
            os.makedirs(self.__outdirectory)
        # Adjustment of plot for saving
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
        plt.savefig(os.path.join(self.__outdirectory, 'combats_matrix.png')) # save combats matrix as a heatmap
        # Adjust and return combats matrix as a heatmap to display
        ids = ['id '+s for s in list(map(str, self.__ids))]
        return go.Heatmap(z=self.__combatsmatrix, x=ids, y=ids, xgap=1, ygap=1, hoverongaps=False,
                          hovertemplate='%{x}<br>%{y}<br>combat: %{z}<br>', name='', colorscale='Viridis')


    def __drawBarChartHumanCombats(self):
        '''
        Visualize statistics about combats for certain human as a bar chart
        '''
        if not os.path.exists(self.__outdirectory):
            os.makedirs(self.__outdirectory)
        self.__buildHumanCombatsDictionary()
        d = self.__combatsdict
        # Check if any combat for certain human takes place
        if len(d) != 0: # at least one combat takes place
            # Adjustment of plot for saving
            fig, ax = plt.subplots(figsize=(12, 9))
            plt.subplots_adjust(left=0.04, bottom=0.04, right=0.96, top=0.96)
            plt.grid()
            ax.bar(np.arange(len(d)), list(d.values()), zorder=2)
            ax.set_xticks(np.arange(len(d)))
            ax.set_xticklabels(list(map(str, d.keys())))
            ax.set_title('Combats for player {}'.format(self.__human))
            ax.set_ylabel('Pixels')
            # Save statistics about combats as a bar chart
            fig.savefig(os.path.join(self.__outdirectory, 'combats___human_{}.png'.format(self.__human)))
            print('Success!')
            # Adjust and return statistics about combats as a bar chart to display
            return go.Bar(x=np.arange(len(d)), y=list(d.values()), marker={'color': 'royalblue'})
        else:
            print('No combats...')
            return go.Bar(x=[], y=[])


    def calculateCombatsStatistics(self):
        '''
        Calculate statistics about combats and visualize it
        '''
        print('Calculate statistics about combats...')
        # Check if any player was detected on the video
        if len(self.__ids) == 0:
            print('No players were detected on the video...')
            return go.Figure()
        else:
            self.__combatsmatrix = np.zeros((len(self.__ids), len(self.__ids)), dtype=np.int)
        self.__buildCombatsMatrix()
        if self.__human is None:
            plotly_object = self.__drawCombatsMatrix()
        else:
            self.__buildHumanCombatsDictionary()
            plotly_object = self.__drawBarChartHumanCombats()
        return plotly_object


def init_argparse():
    '''
    Initialize argparse
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