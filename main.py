
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph
from pyqtgraph import PlotWidget
import pandas as pd
from gui import Ui_MainWindow


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Variables Initialization
        self.isChannel1Open, self.isChannel2Open, self.isChannel3Open = False, False, False
        self.isChannel1Shown, self.isChannel2Shown, self.isChannel3Shown = False, False, False
        self.channel1Signal = pyqtgraph.PlotCurveItem()
        self.channel1TimeReadings = []
        self.channel1AmplitudeReadings = []
        self.channel1PlottedXCoordinates = []
        self.channel1PlottedYCoordinates = []
        self.channel2Signal = pyqtgraph.PlotCurveItem()
        self.channel2TimeReadings = []
        self.channel2AmplitudeReadings = []
        self.channel2PlottedXCoordinates = []
        self.channel2PlottedYCoordinates = []
        self.channel3Signal = pyqtgraph.PlotCurveItem()
        self.channel3TimeReadings = []
        self.channel3AmplitudeReadings = []
        self.channel3PlottedXCoordinates = []
        self.channel3PlottedYCoordinates = []

        # Links of GUI Elements to Methods:

    # Methods


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())