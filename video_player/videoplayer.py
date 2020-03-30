from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QSizePolicy, QSlider, QStyle, QVBoxLayout, QMessageBox
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication
import sys
import os

import constants
import operations
from statdialog import StatDialog
#from mottracker import MOTTracker


class VideoPlayer(QMainWindow):
    '''
    Implement main window (of application) and its behavior
    '''

    def __init__(self, parent=None, width=1024, height=768):
        super(VideoPlayer, self).__init__(parent)
        self.setWindowTitle('SportAISystem 1.0')

        self.__filename = '' # name of videofile

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface) # surface for showing videos

        videoWidget = QVideoWidget() # widget for playing video

        # Connect mediaplayer with slots
        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

        # Play button and its behaviour
        self.playButton = QPushButton()
        self.playButton.setEnabled(False) # hide button before the choice of any video
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.playVideo)

        # Stop button and its behaviour
        self.stopButton = QPushButton()
        self.stopButton.setEnabled(False) # hide button before the choice of any video
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopButton.clicked.connect(self.stopVideo)

        # Slider to visualize the duration of video
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0) # set to start
        self.positionSlider.sliderMoved.connect(self.setPosition)

        # Create and adjust labels
        self.errorLabel = QLabel('')
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        # Labels for duration and total time of video
        self.durationLabel = QLabel()
        self.durationLabel.setText('--:--')
        self.durationLabel.setFixedSize(30, 20)
        self.durationLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.totalLabel = QLabel()
        self.totalLabel.setText('--:--')
        self.totalLabel.setFixedSize(30, 20)

        # Statistics button and its behaviour
        self.statButton = QPushButton('Statistics')
        self.statButton.setToolTip('Calculate statistics about sportsmen')
        self.statButton.clicked.connect(self.pressStatistics)

        # Tracker button and its behaviour
        self.trackButton = QPushButton('ON') # Turn ON the mode of traching video by means of JDE tracker
        self.trackButton.setCheckable(True)
        self.trackButton.setChecked(True)
        self.trackButton.setToolTip('JDE Tracker turned on')
        self.trackButton.clicked.connect(self.trackHumans)

        # Create open action
        openAction = QAction(QIcon('Icons/play-button.png'), '&Open video', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open video')
        openAction.triggered.connect(self.openFile)

        # Create live action
        liveAction = QAction(QIcon('Icons/tv.png'), '&Live stream', self)
        liveAction.setShortcut('Ctrl+L')
        liveAction.setStatusTip('Live stream')

        # Create and adjust exit action
        exitAction = QAction(QIcon('Icons/log-out.png'), '&Quit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        # Create and adjust about action
        aboutAction = QAction(QIcon('Icons/info.png'), '&About program', self)
        aboutAction.setShortcut('Ctrl+A')
        aboutAction.setStatusTip('About program')
        aboutAction.triggered.connect(self.showAboutDialog)

        # Create menu bar with actions
        menuBar = self.menuBar()
        mediaMenu = menuBar.addMenu('&Media')
        mediaMenu.addAction(openAction)
        mediaMenu.addSeparator()
        mediaMenu.addAction(liveAction)
        mediaMenu.addSeparator()
        mediaMenu.addAction(exitAction)
        aboutMenu = menuBar.addMenu('&Help')
        aboutMenu.addAction(aboutAction)

        central_widget = QWidget(self) # widget for window contents
        self.setCentralWidget(central_widget)

        # Collect widgets
        sliderLayout = QHBoxLayout()
        sliderLayout.setContentsMargins(0, 0, 0, 0)
        sliderLayout.addWidget(self.durationLabel)
        sliderLayout.addWidget(self.positionSlider)
        sliderLayout.addWidget(self.totalLabel)
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.stopButton)
        controlLayout.addSpacerItem(QtWidgets.QSpacerItem(100, 10, QtWidgets.QSizePolicy.Expanding))
        controlLayout.addWidget(QLabel('Tracker:'))
        controlLayout.addWidget(self.trackButton)
        controlLayout.addWidget(self.statButton)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(videoWidget)
        mainLayout.addLayout(sliderLayout)
        mainLayout.addLayout(controlLayout)
        mainLayout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        central_widget.setLayout(mainLayout)
        self.resize(width, height)


    def openFile(self):
        self.__filename, _ = QFileDialog.getOpenFileName(self, 'Open videos', os.getcwd(),
                                                         'Videos (*.avi *mp4 *.wmv)')
        if self.__filename:
            if self.trackButton.isChecked(): # JDE Tracker was turned ON
                QApplication.setOverrideCursor(Qt.WaitCursor)
                self.errorLabel.setText('Waiting for tracking the video')
                #jde = MOTTracker(self.__filename, constants.GPU_NUMBER)
                #jde.trackVideo()
                QApplication.restoreOverrideCursor()
                self.errorLabel.setText('')
                tracked_video = os.path.join(constants.RESULTS_FOLDER, self.__filename)
                self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(tracked_video)))
            else: # JDE Tracker was turned OFF
                self.errorLabel.setText('')
                self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.__filename)))
            self.playButton.setEnabled(True)
            self.stopButton.setEnabled(True)
            self.mediaPlayer.pause()


    def exitCall(self):
        sys.exit(0)


    def playVideo(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()


    def stopVideo(self):
        self.mediaPlayer.stop()


    def pressStatistics(self):
        # Set markup file with saved information about bboxes, ids of humans on each frame of video
        markup = os.path.join(constants.RESULTS_FOLDER, os.path.splitext(os.path.basename(self.__filename))[0]+'.txt')
        if os.path.exists(markup):
            st = StatDialog(markup=markup)
            st.exec()
        else:
            self.errorLabel.setText('Cannot find markup file! Please load marked video or mark it using Tracker before')


    def trackHumans(self):
        if self.trackButton.isChecked():
            self.trackButton.setText('ON') # Turn ON tracker
        else:
            self.trackButton.setText('OFF') # Turn OFF tracker


    def showAboutDialog(self):
        '''
        Create 'About program' window
        '''
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText('SportAISystem 1.0')
        msg.setInformativeText('Contacts: sportaisystemyar@gmail.com')
        msg.setWindowTitle('About program')
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()


    def mediaStateChanged(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))


    def positionChanged(self, position):
        self.positionSlider.setValue(position)
        if position >= 0:
            self.durationLabel.setText(operations.time_string(position))


    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)
        if duration >= 0:
            self.totalLabel.setText(operations.time_string(duration))


    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)


    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText('Error: ' + self.mediaPlayer.errorString())