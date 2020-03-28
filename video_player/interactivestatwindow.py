import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tkinter import Tk

import constants


class InteractiveStatWindow:

    def __init__(self, rows=1, cols=1, spacing=0.03, subplot_titles=None):
        self.__rows = rows
        self.__cols = cols
        self.__subplot_titles = subplot_titles
        if (self.__rows==2) and (self.__cols==2):
            self.__figure = make_subplots(rows=self.__rows, cols=self.__cols, column_widths=[0.4, 0.6],
                                          vertical_spacing=spacing, horizontal_spacing=spacing,
                                          specs=[[{}, {"rowspan": 2}],
                                                 [{}, None]],
                                          subplot_titles=subplot_titles)
            self.__width = min(2*constants.OUTPUT_FRAME_SIZE[0], Tk().winfo_screenwidth())
            self.__height = min(2*constants.OUTPUT_FRAME_SIZE[1], Tk().winfo_screenheight())
        if (self.__rows==2) and (self.__cols==1):
            self.__figure = make_subplots(rows=self.__rows, cols=self.__cols, vertical_spacing=spacing,
                                          subplot_titles=subplot_titles)
            self.__width = constants.OUTPUT_FRAME_SIZE[0]
            self.__height = min(2*constants.OUTPUT_FRAME_SIZE[1], Tk().winfo_screenheight())
        if (self.__rows==1) and (self.__cols==2):
            self.__figure = make_subplots(rows=self.__rows, cols=self.__cols, horizontal_spacing=spacing,
                                          subplot_titles=subplot_titles)
            self.__width = min(2*constants.OUTPUT_FRAME_SIZE[0], Tk().winfo_screenwidth())
            self.__height = constants.OUTPUT_FRAME_SIZE[1]


    def addCombatsMatrix(self, combats_matrix):
        if (self.__rows!=1) or (self.__cols!=1):
            self.__figure.add_trace(combats_matrix, row=1, col=2)
            self.__figure.update_yaxes(autorange='reversed', row=1, col=2)
        else:
            self.__figure = go.Figure(combats_matrix)
            self.__figure.update_yaxes(autorange='reversed')
            self.__width = self.__height = constants.OUTPUT_FRAME_SIZE[1]


    def addCombatsBarChart(self, combats_barchart):
        if self.__cols==2:
            self.__figure.add_trace(combats_barchart, row=1, col=2)
            self.__figure.update_traces(hovertemplate='id: %{x}<br>combats: %{y}<br>', name='', row=1, col=2)
        else:
            self.__figure = go.Figure(combats_barchart)
            self.__width = constants.OUTPUT_FRAME_SIZE[0]
            self.__height = constants.OUTPUT_FRAME_SIZE[1]


    def addMotionHeatmap(self, heatmap_image):
        if (self.__rows!=1) or (self.__cols!=1):
            self.__figure.add_trace(heatmap_image, row=1, col=1)
            self.__figure.update_xaxes(showticklabels=False, row=1, col=1)
            self.__figure.update_yaxes(showticklabels=False, row=1, col=1)
            self.__figure.update_traces(hovertemplate='x: %{x}<br>y: %{y}<br>', name='', row=1, col=1)
        else:
            self.__figure = px.imshow(heatmap_image)
            self.__figure.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)
            self.__figure.update_traces(hovertemplate='x: %{x} <br>y: %{y}<br>', name='')
            self.__width = constants.OUTPUT_FRAME_SIZE[0]
            self.__height = constants.OUTPUT_FRAME_SIZE[1]


    def addDistancesBarChart(self, paths_barchart):
        if self.__rows==2:
            self.__figure.add_trace(paths_barchart, row=2, col=1)
            self.__figure.update_traces(hovertemplate='id: %{y}<br>dist: %{x}<br>', name='', row=2, col=1)
        else:
            if self.__cols==2:
                self.__figure.add_trace(paths_barchart, row=1, col=1)
                self.__figure.update_traces(hovertemplate='id: %{y}<br>dist: %{x}<br>', name='', row=1, col=1)
            else:
                self.__figure = go.Figure(paths_barchart)
                self.__figure.update_traces(hovertemplate='id: %{y}<br>dist: %{x} px<br>', name='')
                self.__width = constants.OUTPUT_FRAME_SIZE[0]
                self.__height = constants.OUTPUT_FRAME_SIZE[1]


    def __adjustInteractiveWindowSize(self):
        if (self.__rows!=1) or (self.__cols!=1):
            self.__figure.update_layout(width=self.__width, height=self.__height, margin=dict(l=5, r=5, b=5, t=45))
        else:
            self.__figure.update_layout(title=self.__subplot_titles[0], width=self.__width, height=self.__height,
                                        margin=dict(l=5, r=5, b=5, t=45))


    def show(self):
        self.__adjustInteractiveWindowSize()
        return self.__figure.show()