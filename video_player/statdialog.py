import os
import shutil
from PyQt5.QtWidgets import QDialog, QCheckBox, QVBoxLayout, QHBoxLayout, QRadioButton, QGroupBox, QSpinBox, \
    QLineEdit, QLabel, QPushButton, QSplitter, QFileDialog, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

import constants
from combatscounter import CombatsCounter
from emailsending import EMailSending
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

        self.setWindowIcon(QIcon('Icons/statistics.png'))

        # Calculate button and its behaviour
        self.calculatePushButton = QPushButton('Calculate')
        self.calculatePushButton.clicked.connect(self.calculateStatistics)

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
        self.remoteRadioButton = QRadioButton('E-mail')

        # Create savepath button and its behaviour
        self.savepathButton = QPushButton('...')
        self.savepathButton.clicked.connect(self.chooseDirectory)
        self.savepathButton.setFixedWidth(25)

        self.emailLineEdit = QLineEdit()

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
        mainLayout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        self.setLayout(mainLayout)

        # Adjust dialog window
        self.setMinimumWidth(350)
        self.setWindowTitle('Videoanalysis')

        if not os.path.exists(constants.STATISTICS_FOLDER):
            os.makedirs(constants.STATISTICS_FOLDER)
        self.setLocalDirectory(constants.STATISTICS_FOLDER)


    def allRadioButtonToggled(self):
        self.humanSpinBox.setDisabled(True)
        self.humanSpinBox.setToolTip('')


    def personRadioButtonToggled(self):
        self.humanSpinBox.setDisabled(False)
        self.humanSpinBox.setToolTip('Choose the number of human')


    def setLocalDirectory(self, str_path):
        self.__dirname = str_path
        if len(self.__dirname) > 44:
            reduced_dirname = '...{}'.format(str(self.__dirname)[-41:])
        else:
            reduced_dirname = str(self.__dirname)
        self.savepathLabel.setText(reduced_dirname)
        self.savepathLabel.setToolTip(str(self.__dirname))


    def chooseDirectory(self):
        self.__dirname = QFileDialog.getExistingDirectory(self, 'Choose directory', os.getcwd(), QFileDialog.ShowDirsOnly)
        if self.__dirname:
            self.setLocalDirectory(self.__dirname)
            self.errorLabel.setText('')


    def calculateStatistics(self):
        self.errorLabel.setText('')
        if not (self.heatmapCheckBox.isChecked() or self.pathsCheckBox.isChecked()
                or self.combatsCheckBox.isChecked()): # None options among statistics were checked
            self.errorLabel.setText('Please choose almost one value of statistics to calculate')
        else:
            if self.__markup: # check if markup file was loaded
                if self.__dirname: # check if directory for saving statistics was created
                    if not os.path.exists(self.__dirname):
                        os.makedirs(self.__dirname)
                    statdir = os.path.join(self.__dirname, os.path.splitext(os.path.basename(self.__markup))[0])
                    '''if not os.path.exists(statdir):
                        os.makedirs(statdir)
                    else:
                        shutil.rmtree(statdir)
                        os.makedirs(statdir)'''
                    if os.path.exists(statdir):
                        shutil.rmtree(statdir)
                    os.makedirs(statdir)
                    if self.personRadioButton.isChecked():
                        human = self.humanSpinBox.value()
                    else:
                        human = None
                    # Calculate statistics
                    QApplication.setOverrideCursor(Qt.WaitCursor) # start calculating
                    if self.heatmapCheckBox.isChecked():
                        mh = MotionHeatmap(markup_file=self.__markup, out_dir=statdir, human_number=human)
                        mh.buildHeatmap()
                    if self.pathsCheckBox.isChecked():
                        mt = MotionTrajectories(markup_file=self.__markup, out_dir=statdir, human_number=human)
                        mt.calculateTraceStatistics()
                    if self.combatsCheckBox.isChecked():
                        comb_acc = CombatsCounter(markup_file=self.__markup, out_dir=statdir, human_number=human)
                        comb_acc.calculateCombatsStatistics()
                    if self.remoteRadioButton.isChecked():
                        email = self.emailLineEdit.text()
                        if email:
                            sending = EMailSending()
                            content = [os.path.join(os.path.abspath(statdir), file) for file in os.listdir(statdir)]
                            sending.sendEMail([email], content)
                            self.errorLabel.setText('Files with statistics values were successfully sent by e-mail')
                        else:
                            self.errorLabel.setText('Please write down email address')
                    else:
                        self.errorLabel.setText('Files with statistics values were loaded in local directory')
                    QApplication.restoreOverrideCursor() # finish calculating
                else:
                    self.errorLabel.setText('Please choose the directory to save')
            else:
                self.errorLabel.setText('Cannot load the markup file')