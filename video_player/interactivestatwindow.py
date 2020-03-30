import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tkinter import Tk

import constants


class InteractiveStatWindow:
    '''
    Implement class to display widgets with calculated statistics as an interactive window (table) in browser
    '''

    def __init__(self, rows=1, cols=1, spacing=0.03, subplot_titles=None):
        '''
        Constructor
        :param rows: amount of rows to place widgets with calculated statistics
        :param cols: amount of columns to place widgets with calculated statistics
        :param spacing: distance between different widgets
        :param subplot_titles: titles of widgets
        '''
        self.__rows = rows
        self.__cols = cols
        self.__subplot_titles = subplot_titles
        # Complex interactive window = table 2x2 of widgets with calculated statistics
        if (self.__rows==2) and (self.__cols==2):
            self.__figure = make_subplots(rows=self.__rows, cols=self.__cols, column_widths=[0.4, 0.6],
                                          vertical_spacing=spacing, horizontal_spacing=spacing,
                                          specs=[[{}, {"rowspan": 2}],
                                                 [{}, None]],
                                          subplot_titles=subplot_titles)
            # Set size of interactive window
            self.__width = min(2*constants.OUTPUT_FRAME_SIZE[0], Tk().winfo_screenwidth())
            self.__height = min(2*constants.OUTPUT_FRAME_SIZE[1], Tk().winfo_screenheight())
        # Complex interactive window = table 2x1 of widgets with calculated statistics
        if (self.__rows==2) and (self.__cols==1):
            self.__figure = make_subplots(rows=self.__rows, cols=self.__cols, vertical_spacing=spacing,
                                          subplot_titles=subplot_titles)
            # Set size of interactive window
            self.__width = constants.OUTPUT_FRAME_SIZE[0]
            self.__height = min(2*constants.OUTPUT_FRAME_SIZE[1], Tk().winfo_screenheight())
        # Complex interactive window = table 1x2 of widgets with calculated statistics
        if (self.__rows==1) and (self.__cols==2):
            self.__figure = make_subplots(rows=self.__rows, cols=self.__cols, horizontal_spacing=spacing,
                                          subplot_titles=subplot_titles)
            # Set size of interactive window
            self.__width = min(2*constants.OUTPUT_FRAME_SIZE[0], Tk().winfo_screenwidth())
            self.__height = constants.OUTPUT_FRAME_SIZE[1]


    def addCombatsMatrix(self, combats_matrix):
        '''
        Add confusion matrix of combats between players into interactive window (table)
        :param combats_matrix: confusion matrix of combats between players
        '''
        if (self.__rows!=1) or (self.__cols!=1):
            # Add combats matrix into complex interactive window
            self.__figure.add_trace(combats_matrix, row=1, col=2)
            # Adjust combats matrix to display
            self.__figure.update_yaxes(autorange='reversed', row=1, col=2)
        else:
            # Display only the combats matrix
            self.__figure = go.Figure(combats_matrix)
            # Adjust combats matrix to display
            self.__figure.update_yaxes(autorange='reversed')
            # Set size of interactive window
            self.__width = self.__height = constants.OUTPUT_FRAME_SIZE[1]


    def addCombatsBarChart(self, combats_barchart):
        '''
        Add bar chart of combats (with players who has combats with chosen one) into interactive window (table)
        :param combats_barchart: bar chart of combats
        '''
        if self.__cols==2:
            # Add bar chart of combats into complex interactive window
            self.__figure.add_trace(combats_barchart, row=1, col=2)
            # Adjust bar chart of combats to display
            self.__figure.update_traces(hovertemplate='id: %{x}<br>combats: %{y}<br>', name='', row=1, col=2)
        else:
            # Display only the bar chart of combats
            self.__figure = go.Figure(combats_barchart)
            # Set size of interactive window
            self.__width = constants.OUTPUT_FRAME_SIZE[0]
            self.__height = constants.OUTPUT_FRAME_SIZE[1]


    def addMotionHeatmap(self, heatmap_image):
        '''
        Add heatmap of motion of players into interactive window (table)
        :param heatmap_image: heatmap of motion
        '''
        if (self.__rows!=1) or (self.__cols!=1):
            # Add heatmap of motion into complex interactive window
            self.__figure.add_trace(heatmap_image, row=1, col=1)
            # Adjust heatmap of motion to display
            self.__figure.update_xaxes(showticklabels=False, row=1, col=1)
            self.__figure.update_yaxes(showticklabels=False, row=1, col=1)
            self.__figure.update_traces(hovertemplate='x: %{x}<br>y: %{y}<br>', name='', row=1, col=1)
        else:
            # Display only the heatmap of motion
            self.__figure = px.imshow(heatmap_image)
            # Adjust heatmap of motion to display
            self.__figure.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)
            self.__figure.update_traces(hovertemplate='x: %{x} <br>y: %{y}<br>', name='')
            # Set size of interactive window
            self.__width = constants.OUTPUT_FRAME_SIZE[0]
            self.__height = constants.OUTPUT_FRAME_SIZE[1]


    def addDistancesBarChart(self, paths_barchart):
        '''
        Add bar chart of distances of players into interactive window (table)
        :param paths_barchart: bar chart of distances
        '''
        if self.__rows==2:
            # Add bar chart of distances into interactive table of size 2x1 or 2x2
            self.__figure.add_trace(paths_barchart, row=2, col=1)
            # Adjust bar chart of distances to display
            self.__figure.update_traces(hovertemplate='id: %{y}<br>dist: %{x}<br>', name='', row=2, col=1)
        else:
            if self.__cols==2:
                # Add bar chart of distances into interactive table of size 1x2
                self.__figure.add_trace(paths_barchart, row=1, col=1)
                # Adjust bar chart of distances to display
                self.__figure.update_traces(hovertemplate='id: %{y}<br>dist: %{x}<br>', name='', row=1, col=1)
            else:
                # Display only the bar chart of distances
                self.__figure = go.Figure(paths_barchart)
                # Adjust bar chart of distances to display
                self.__figure.update_traces(hovertemplate='id: %{y}<br>dist: %{x}<br>', name='')
                # Set size of interactive window
                self.__width = constants.OUTPUT_FRAME_SIZE[0]
                self.__height = constants.OUTPUT_FRAME_SIZE[1]


    def __adjustDisplayInteractiveWindow(self, title=None):
        '''
        Adjust an interactive window to display
        :param title: title of interactive window
        '''
        if (self.__rows!=1) or (self.__cols!=1):
            # Complex interactive window
            if title:
                self.__figure.update_layout(width=self.__width, height=self.__height, margin=dict(l=5, r=5, b=5, t=45),
                                            title_text=title, title_x=0.0)
            else:
                self.__figure.update_layout(width=self.__width, height=self.__height, margin=dict(l=5, r=5, b=5, t=45))
        else:
            # in case of display only one widget of calculated statistics
            self.__figure.update_layout(title=self.__subplot_titles[0], width=self.__width, height=self.__height,
                                        margin=dict(l=5, r=5, b=5, t=45))


    def show(self, title=None):
        '''
        Show interactive window
        :param title: title of interactive window
        '''
        self.__adjustDisplayInteractiveWindow(title)
        return self.__figure.show()