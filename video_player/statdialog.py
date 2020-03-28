import os
import shutil
import plotly.graph_objects as go
from PyQt5.QtWidgets import QDialog, QCheckBox, QVBoxLayout, QHBoxLayout, QRadioButton, QGroupBox, QSpinBox, \
    QLineEdit, QLabel, QPushButton, QSplitter, QFileDialog, QSizePolicy
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
        super(StatDialog, self).__init__(parent)

        self.__markup = markup
        self.__dirname = ''

        self.__showHeatmapFlag = False
        self.__showCombatsFlag = False
        self.__showPathsFlag = False

        self.__recountHeatmap = True
        self.__recountCombats = True
        self.__recountPaths = True

        self.__human = None
        self.__predhuman = 0

        self.__heatmapImage = None
        self.__pathsImages = None
        self.__combatsImage = None


        self.setWindowIcon(QIcon('Icons/statistics.png'))

        # Calculate button and its behaviour
        self.calculatePushButton = QPushButton('Calculate')
        self.calculatePushButton.clicked.connect(self.calculateStatistics)

        # Show results button and its behaviour
        self.showPushButton = QPushButton('Show results')
        self.showPushButton.setEnabled(False)
        self.showPushButton.clicked.connect(self.showResults)

        # Create and adjust labels
        self.errorLabel = QLabel('')
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.savepathLabel = QLabel('Please choose directory')
        self.savepathLabel.setToolTip('')

        # Create and adjust checkboxes
        self.heatmapCheckBox = QCheckBox('Heatmap', self)
        self.heatmapCheckBox.setToolTip('Motion heatmap on the field')
        self.heatmapCheckBox.setChecked(True)
        self.combatsCheckBox = QCheckBox('Combats', self)
        self.combatsCheckBox.setToolTip('Number of combats between rivals')
        self.pathsCheckBox = QCheckBox('Motion paths', self)
        self.pathsCheckBox.setToolTip('Motion trajectories and their lenght')

        # Create and adjust spiboxes
        self.humanSpinBox = QSpinBox()
        self.humanSpinBox.setMinimum(1)

        # Create and adjust radiobuttons
        self.allRadioButton = QRadioButton('For all people')
        self.allRadioButton.setChecked(True)
        self.personRadioButton = QRadioButton('For specific person')
        self.allRadioButton.toggled.connect(self.allRadioButtonToggled)
        self.personRadioButton.toggled.connect(self.personRadioButtonToggled)
        self.allRadioButtonToggled()
        self.localRadioButton = QRadioButton('Local saving')
        self.localRadioButton.setChecked(True)
        self.localRadioButton.toggled.connect(self.localRadioButtonToggled)
        self.remoteRadioButton = QRadioButton('E-mail')
        self.remoteRadioButton.toggled.connect(self.remoteRadioButtonToggled)

        # Create savepath button and its behaviour
        self.savepathButton = QPushButton('...')
        self.savepathButton.clicked.connect(self.chooseDirectory)
        self.savepathButton.setFixedWidth(25)

        self.emailLineEdit = QLineEdit()
        self.__validator = QRegExpValidator(QRegExp('[^@]+@[^@]+\.[^@]+'))
        self.emailLineEdit.setValidator(self.__validator)
        self.emailLineEdit.textChanged.connect(self.validateEMail)

        # Create groupboxes and collect elements into them
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
        state = self.__validator.validate(self.emailLineEdit.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = '#c4df9b'  # green
        else:
            if not self.emailLineEdit.text():
                color = '#ffffff' # white
            else:
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
                    if os.path.exists(statdir):
                        shutil.rmtree(statdir)
                    os.makedirs(statdir)
                    if self.personRadioButton.isChecked():
                        self.__human = self.humanSpinBox.value()
                    else:
                        self.__human = None
                    # Calculate statistics
                    QApplication.setOverrideCursor(Qt.WaitCursor) # start calculating
                    if self.heatmapCheckBox.isChecked():
                        self.__showHeatmapFlag = True
                        mh = MotionHeatmap(markup_file=self.__markup, out_dir=statdir, human_number=self.__human)
                        self.__heatmapImage = mh.buildHeatmap()
                    if self.pathsCheckBox.isChecked():
                        self.__showPathsFlag = True
                        mt = MotionTrajectories(markup_file=self.__markup, out_dir=statdir, human_number=self.__human)
                        self.__pathsBarChart = mt.calculateTraceStatistics()
                    if self.combatsCheckBox.isChecked():
                        self.__showCombatsFlag = True
                        comb_acc = CombatsCounter(markup_file=self.__markup, out_dir=statdir, human_number=self.__human)
                        self.__combatsData = comb_acc.calculateCombatsStatistics()
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
                    self.showPushButton.setEnabled(True)
                else:
                    self.errorLabel.setText('Please choose the directory to save')
            else:
                self.errorLabel.setText('Cannot load the markup file')


    def showResults(self):
        self.errorLabel.setText('')
        if self.__showPathsFlag and not self.__human:  # Show Distances bar chart
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
                fig = go.Figure(self.__pathsBarChart)
            return
        # Hide Distances bar chart
        if self.__showHeatmapFlag and self.__showCombatsFlag: # Show Heatmap, show Combats
            if self.__human:
                title = 'Combats for player {}'.format(self.__human)
            else:
                title = 'Combats matrix'
            stat_window = InteractiveStatWindow(rows=1, cols=2, subplot_titles=['Motion heatmap', title])
            stat_window.addMotionHeatmap(go.Image(z=self.__heatmapImage))  # Display Heatmap
            if self.__human:
                stat_window.addCombatsBarChart(self.__combatsData)
            else:
                stat_window.addCombatsMatrix(self.__combatsData)
            stat_window.show()
        if self.__showHeatmapFlag and not self.__showCombatsFlag:  # Show Heatmap only
            stat_window = InteractiveStatWindow(subplot_titles=['Motion heatmap'])
            stat_window.addMotionHeatmap(self.__heatmapImage)  # Display Heatmap
            stat_window.show()
        if not self.__showHeatmapFlag and self.__showCombatsFlag:  # Show Combats only
            if self.__human:
                title = 'Combats for player {}'.format(self.__human)
            else:
                title = 'Combats matrix'
            stat_window = InteractiveStatWindow(subplot_titles=[title])
            if self.__human:
                stat_window.addCombatsBarChart(self.__combatsData)
            else:
                stat_window.addCombatsMatrix(self.__combatsData)
            stat_window.show()