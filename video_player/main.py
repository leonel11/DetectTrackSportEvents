import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from videoplayer import VideoPlayer


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('Icons/voleyball-player.png'))
    player = VideoPlayer(width=800, height=600)
    player.show()
    sys.exit(app.exec_())