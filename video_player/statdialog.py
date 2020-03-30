import os
import shutil
import plotly.graph_objects as go
from PyQt5.QtWidgets import QDialog, QCheckBox, QVBoxLayout, QHBoxLayout, QRadioButton, QGroupBox, QSpinBox, QLabel, \
    QLineEdit, QPushButton, QSplitter, QFileDialog, QSizePolicy
from PyQt5.QtGui import QIcon, QRegExpValidator, QValidator
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtWidgets import QApplication

import constants
from combatscounter import CombatsCounter
from emailsending import EMailSending
from interactivestatwindow import InteractiveStatWindow
from motionheatmap import MotionHeatmap
from motiontrajectories import MotionTrajectories


class StatDialog(QDialog):
    '''
    Implement dialog window and its behaviour for calculation of statistics
    '''

    def __init__(self, parent=None, markup=None):
        '''
        Constructor
        :param markup: file with saved information about bboxes, ids of humans on each frame of video
        '''
        super(StatDialog, self).__init__(parent)

        self.__markup = markup # markup file
        self.__dirname = '' # directory to store calculated statistics

        # Flags of display statistics into interactive window
        self.__showHeatmapFlag = False
        self.__showCombatsFlag = False
        self.__showPathsFlag = False

        # Flags of calculation of statistics to avoid its recalculation
        self.__recountHeatmap = False
        self.__recountCombats = False
        self.__recountPaths = False

        self.__human = None # id of human
        self.__humandist = 0.0  # distance which human has overcome
        self.__prevhuman = 0 # id of human for whom statistics were calculated on previous step

        self.__isFirstLaunchWindow = True # flag of first launch of calculation of statistics

        # Components of interactive window
        self.__heatmapImage = None
        self.__pathsImages = None
        self.__combatsImage = None

        self.setWindowIcon(QIcon('Icons/statistics.png'))

        # Calculate button and its behaviour
        self.calculatePushButton = QPushButton('Calculate')
        self.calculatePushButton.clicked.connect(self.calculateStatistics)

        # Show results button and its behaviour
        self.showPushButton = QPushButton('Show results')
        self.showPushButton.setEnabled(False) # nothing to show in interactive window before the calculation
        self.showPushButton.clicked.connect(self.showResults)

        # Create and adjust labels
        self.errorLabel = QLabel('')
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.savepathLabel = QLabel('Please choose directory')
        self.savepathLabel.setToolTip('')

        # Create and adjust checkboxes to choose statistics for calculation
        self.heatmapCheckBox = QCheckBox('Heatmap', self)
        self.heatmapCheckBox.setToolTip('Motion heatmap on the field')
        self.heatmapCheckBox.setChecked(True)
        self.combatsCheckBox = QCheckBox('Combats', self)
        self.combatsCheckBox.setToolTip('Number of combats between rivals')
        self.pathsCheckBox = QCheckBox('Motion paths', self)
        self.pathsCheckBox.setToolTip('Motion trajectories and their lenght')

        # Flags of checkboxes, which were chosen to calculate statistics, to avoid any recalculation
        self.__prevHeatmapChecked = False
        self.__prevCombatsChecked = False
        self.__prevPathsChecked = False

        # Create and adjust spibox
        self.humanSpinBox = QSpinBox()
        self.humanSpinBox.setMinimum(1)

        # Create and adjust radiobuttons
        # Radiobuttons for humans to calculate statistics
        self.allRadioButton = QRadioButton('For all people')
        self.allRadioButton.setChecked(True)
        self.personRadioButton = QRadioButton('For specific person')
        self.allRadioButton.toggled.connect(self.allRadioButtonToggled)
        self.personRadioButton.toggled.connect(self.personRadioButtonToggled)
        self.allRadioButtonToggled()
        # Radiobuttons for saving statistics or sending it as an e-mail
        self.localRadioButton = QRadioButton('Local saving')
        self.localRadioButton.setChecked(True)
        self.localRadioButton.toggled.connect(self.localRadioButtonToggled)
        self.remoteRadioButton = QRadioButton('E-mail')
        self.remoteRadioButton.toggled.connect(self.remoteRadioButtonToggled)

        # Create savepath button and its behaviour
        self.savepathButton = QPushButton('...')
        self.savepathButton.clicked.connect(self.chooseDirectory)
        self.savepathButton.setFixedWidth(25)

        # Create line edit to type e-mail for sending information
        self.emailLineEdit = QLineEdit()
        # Attach e-mail validator
        self.__validator = QRegExpValidator(QRegExp('[^@]+@[^@]+\.[^@]+'))
        self.emailLineEdit.setValidator(self.__validator)
        self.emailLineEdit.textChanged.connect(self.validateEMail)

        # Collect radiobuttons and checkboxes
        statGroupBox = QGroupBox('Sport statistics')
        statLayout = QVBoxLayout()
        statLayout.addWidget(self.heatmapCheckBox)
        statLayout.addWidget(self.combatsCheckBox)
        statLayout.addWidget(self.pathsCheckBox)
        statLayout.addStretch(1)
        statGroupBox.setLayout(statLayout)
        optionsGroupBox = QGroupBox('Options')
        optionsLayout = QVBoxLayout()
        optionsLayout.addWidget(self.allRadioButton)
        optionsLayout.addWidget(self.personRadioButton)
        optionsLayout.addWidget(self.humanSpinBox)
        optionsLayout.addStretch(1)
        optionsGroupBox.setLayout(optionsLayout)
        saveLayout = QHBoxLayout()
        saveLayout.addWidget(self.savepathLabel)
        saveLayout.addWidget(self.savepathButton)
        sendGroupBox = QGroupBox('Sending', alignment=Qt.AlignHCenter)
        sendLayout = QVBoxLayout()
        sendLayout.addWidget(self.localRadioButton)
        sendLayout.addLayout(saveLayout)
        sendLayout.addWidget(self.remoteRadioButton)
        sendLayout.addWidget(self.emailLineEdit)
        sendGroupBox.setLayout(sendLayout)

        # Collect widgets
        vertLayout = QHBoxLayout()
        vertLayout.addWidget(statGroupBox)
        vertLayout.addWidget(optionsGroupBox)
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(vertLayout)
        mainLayout.addWidget(QSplitter(Qt.Horizontal))
        mainLayout.addWidget(sendGroupBox)
        mainLayout.addWidget(QSplitter(Qt.Horizontal))
        mainLayout.addWidget(self.calculatePushButton)
        mainLayout.addWidget(self.showPushButton)
        mainLayout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        self.setLayout(mainLayout)

        # Adjust dialog window
        self.setMinimumWidth(350)
        self.setWindowTitle('Videoanalysis')

        if not os.path.exists(constants.STATISTICS_FOLDER):
            os.makedirs(constants.STATISTICS_FOLDER)
        self.setLocalDirectory(constants.STATISTICS_FOLDER)


    def validateEMail(self):
        '''
        Check correctness of e-mail
        :return: state if e-mail is valid or not
        '''
        state = self.__validator.validate(self.emailLineEdit.text(), 0)[0]
        if state == QValidator.Acceptable: # e-mail is valid
            color = '#c4df9b'  # green
        else:
            if not self.emailLineEdit.text(): # empty field for typing an e-mail
                color = '#ffffff' # white
            else: # e-mail is invalid
                color = '#f6989d'  # red
        self.emailLineEdit.setStyleSheet('QLineEdit { background-color: %s }' % color)
        return state


    def allRadioButtonToggled(self):
        self.humanSpinBox.setDisabled(True)
        self.humanSpinBox.setToolTip('')


    def personRadioButtonToggled(self):
        self.humanSpinBox.setDisabled(False)
        self.humanSpinBox.setToolTip('Choose the number of human')


    def localRadioButtonToggled(self):
        self.emailLineEdit.setStyleSheet('QLineEdit { background-color: #ffffff }')


    def remoteRadioButtonToggled(self):
        self.validateEMail()


    def setLocalDirectory(self, str_path):
        '''
        Display local directory for saving calculated statistics
        :param str_path: chosen local directory
        '''
        self.__dirname = str_path
        if len(self.__dirname) > 44:
            reduced_dirname = '...{}'.format(str(self.__dirname)[-41:])
        else:
            reduced_dirname = str(self.__dirname)
        self.savepathLabel.setText(reduced_dirname)
        self.savepathLabel.setToolTip(str(self.__dirname))


    def chooseDirectory(self):
        self.__dirname = QFileDialog.getExistingDirectory(self, 'Choose directory', os.getcwd(),
                                                          QFileDialog.ShowDirsOnly)
        if self.__dirname:
            self.setLocalDirectory(self.__dirname)
            self.errorLabel.setText('')


    def checkStatisticsRecount(self):
        '''
        Check what statistics are needed to recount
        '''
        if (not self.__prevHeatmapChecked or self.__human != self.__prevhuman) and self.heatmapCheckBox.isChecked():
            self.__recountHeatmap = True
        else:
            self.__recountHeatmap = False
        if (not self.__prevCombatsChecked or self.__human != self.__prevhuman) and self.combatsCheckBox.isChecked():
            self.__recountCombats = True
        else:
            self.__recountCombats = False
        if (not self.__prevPathsChecked or self.__human != self.__prevhuman) and self.pathsCheckBox.isChecked():
            self.__recountPaths = True
        else:
            self.__recountPaths = False


    def saveCalculatedStatisticsStates(self):
        '''
        Set flags what statistics are checked to calculate
        '''
        if self.heatmapCheckBox.isChecked():
            self.__prevHeatmapChecked = True
        else:
            self.__prevHeatmapChecked = False
        if self.combatsCheckBox.isChecked():
            self.__prevCombatsChecked = True
        else:
            self.__prevCombatsChecked = False
        if self.pathsCheckBox.isChecked():
            self.__prevPathsChecked = True
        else:
            self.__prevPathsChecked = False


    def calculateStatistics(self):
        self.errorLabel.setText('')
        self.__showHeatmapFlag = False
        self.__showCombatsFlag = False
        self.__showPathsFlag = False
        if not (self.heatmapCheckBox.isChecked() or self.pathsCheckBox.isChecked()
                or self.combatsCheckBox.isChecked()): # None options among statistics were checked
            self.errorLabel.setText('Please choose almost one value of statistics to calculate')
        else:
            if self.__markup: # check if markup file was loaded
                if self.__dirname: # check if directory for saving statistics was created
                    if not os.path.exists(self.__dirname):
                        os.makedirs(self.__dirname)
                    statdir = os.path.join(self.__dirname, os.path.splitext(os.path.basename(self.__markup))[0])
                    if self.__isFirstLaunchWindow:
                        # Create empty folder to store statistics
                        print('Create directory to store statistics...')
                        if os.path.exists(statdir):
                            shutil.rmtree(statdir)
                        os.makedirs(statdir)
                        print('Done: \t {}'.format(statdir))
                    # Get id of human for whom it is needed to calculate statistics
                    if self.personRadioButton.isChecked():
                        self.__human = self.humanSpinBox.value() # id of human
                    else:
                        self.__human = None # all humans
                    self.checkStatisticsRecount()
                    # Calculate statistics
                    QApplication.setOverrideCursor(Qt.WaitCursor) # start calculating
                    # Calculation of motion heatmap
                    if self.heatmapCheckBox.isChecked():
                        if self.__recountHeatmap:
                            mh = MotionHeatmap(markup_file=self.__markup, out_dir=statdir, human_number=self.__human)
                            self.__heatmapImage = mh.buildHeatmap()
                        else:
                            if not self.__isFirstLaunchWindow and self.__prevHeatmapChecked:
                                print('Motion heatmap has already built!')
                        self.__showHeatmapFlag = True
                        self.__prevHeatmapChecked = True
                    else:
                        self.__prevHeatmapChecked = False
                    # Calculation of motion trajectories and covered distances
                    if self.pathsCheckBox.isChecked():
                        if self.__recountPaths:
                            mt = MotionTrajectories(markup_file=self.__markup, out_dir=statdir, human_number=self.__human)
                            self.__pathsBarChart = mt.calculateTraceStatistics()
                            self.__humandist = mt.getDistance(self.__human)
                        else:
                            if not self.__isFirstLaunchWindow and self.__prevPathsChecked:
                                print('Statistics about paths and distances have already counted!')
                        self.__showPathsFlag = True
                        self.__prevPathsChecked = True
                    else:
                        self.__prevPathsChecked = False
                    # Calculation of combats between players
                    if self.combatsCheckBox.isChecked():
                        if self.__recountCombats:
                            comb_acc = CombatsCounter(markup_file=self.__markup, out_dir=statdir, human_number=self.__human)
                            self.__combatsData = comb_acc.calculateCombatsStatistics()
                        else:
                            if not self.__isFirstLaunchWindow and self.__prevCombatsChecked:
                                print('Statistics about combats have already calculated!')
                        self.__showCombatsFlag = True
                        self.__prevCombatsChecked = True
                    else:
                        self.__prevCombatsChecked = False
                    # Sending calculated statistics as an e-mail
                    if self.remoteRadioButton.isChecked():
                        email = self.emailLineEdit.text()
                        if email and (self.validateEMail() == QValidator.Acceptable):
                            sending = EMailSending()
                            content = [os.path.join(os.path.abspath(statdir), file) for file in os.listdir(statdir)]
                            sending.sendEMail([email], content)
                            self.errorLabel.setText('Files with statistics values were successfully sent by e-mail')
                        else:
                            self.errorLabel.setText('Please write down valid email address')
                    else:
                        self.errorLabel.setText('Files with statistics values were loaded in local directory')
                    QApplication.restoreOverrideCursor() # finish calculating
                    self.__prevhuman = self.__human
                    self.__isFirstLaunchWindow = False
                    self.showPushButton.setEnabled(True)
                else:
                    self.errorLabel.setText('Please choose the directory to save')
            else:
                self.errorLabel.setText('Cannot load the markup file')


    def showResults(self):
        self.errorLabel.setText('')
        distance_title = None
        if self.__showPathsFlag:
            if not self.__human: # Show Distances bar chart
                if self.__showHeatmapFlag and self.__showCombatsFlag:  # Show Heatmap, show Combats, show Distances
                    stat_window = InteractiveStatWindow(rows=2, cols=2, subplot_titles=['Motion heatmap', 'Combats matrix',
                                                                                        'Covered distances'])
                    stat_window.addMotionHeatmap(go.Image(z=self.__heatmapImage))  # Display Heatmap
                    stat_window.addDistancesBarChart(self.__pathsBarChart)  # Display Distances
                    stat_window.addCombatsMatrix(self.__combatsData)  # Display Combats matrix
                    stat_window.show()
                if self.__showHeatmapFlag and not self.__showCombatsFlag:  # Show Heatmap, show Distances
                    stat_window = InteractiveStatWindow(rows=2, cols=1,
                                                        subplot_titles=['Motion heatmap', 'Covered distances'])
                    stat_window.addMotionHeatmap(go.Image(z=self.__heatmapImage))  # Display Heatmap
                    stat_window.addDistancesBarChart(self.__pathsBarChart)  # Display Distances
                    stat_window.show()
                if not self.__showHeatmapFlag and self.__showCombatsFlag:  # Show Combats, show Distances
                    stat_window = InteractiveStatWindow(rows=1, cols=2,
                                                        subplot_titles=['Covered distances', 'Combats matrix'])
                    stat_window.addDistancesBarChart(self.__pathsBarChart)  # Display Distances
                    stat_window.addCombatsMatrix(self.__combatsData)  # Display Combats matrix
                    stat_window.show()
                if not self.__showHeatmapFlag and not self.__showCombatsFlag:  # Show Distances only
                    stat_window = InteractiveStatWindow(subplot_titles=['Covered distances'])
                    stat_window.addDistancesBarChart(self.__pathsBarChart)  # Display Distances
                    stat_window.show()
                return
            else: # Show distance for player in title
                distance_title = 'Id {}, distance: {:.2f}'.format(self.__human, self.__humandist)
        # Hide Distances bar chart
        if self.__showHeatmapFlag and self.__showCombatsFlag: # Show Heatmap, show Combats
            if self.__human and not distance_title:
                heatmap_title = 'Motion heatmap for id {}'.format(self.__human)
                combats_title = 'Combats for id {}'.format(self.__human)
            else:
                heatmap_title = 'Motion heatmap'
                combats_title = 'Combats matrix'
            stat_window = InteractiveStatWindow(rows=1, cols=2, subplot_titles=[heatmap_title, combats_title])
            stat_window.addMotionHeatmap(go.Image(z=self.__heatmapImage))  # Display Heatmap
            if self.__human:
                stat_window.addCombatsBarChart(self.__combatsData)
            else:
                stat_window.addCombatsMatrix(self.__combatsData)
            stat_window.show(distance_title)
        if self.__showHeatmapFlag and not self.__showCombatsFlag:  # Show Heatmap only
            if self.__human:
                title = 'Motion heatmap for id {}'.format(self.__human)
            else:
                title = 'Motion heatmap'
            stat_window = InteractiveStatWindow(subplot_titles=[title])
            stat_window.addMotionHeatmap(self.__heatmapImage)  # Display Heatmap
            stat_window.show()
        if not self.__showHeatmapFlag and self.__showCombatsFlag:  # Show Combats only
            if self.__human:
                title = 'Combats for id {}'.format(self.__human)
            else:
                title = 'Combats matrix'
            stat_window = InteractiveStatWindow(subplot_titles=[title])
            if self.__human:
                stat_window.addCombatsBarChart(self.__combatsData)
            else:
                stat_window.addCombatsMatrix(self.__combatsData)
            stat_window.show()