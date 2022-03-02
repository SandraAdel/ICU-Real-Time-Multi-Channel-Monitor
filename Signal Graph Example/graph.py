# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'graph.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph
from pyqtgraph import PlotWidget
import pandas as pd


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(833, 416)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(0, 0, 75, 23))
        self.pushButton.setObjectName("pushButton")
        # Linking the button to getFile function
        self.pushButton.clicked.connect(self.openFile)

        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(110, 80, 571, 231))
        self.widget.setObjectName("widget")

        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        self.widget1 = QtWidgets.QWidget(self.widget)
        self.widget1.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.widget1.setObjectName("widget1")
        self.gridLayout.addWidget(self.widget1, 0, 0, 1, 1)

        self.verticalSlider = QtWidgets.QSlider(self.widget)
        self.verticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider.setObjectName("verticalSlider")
        self.gridLayout.addWidget(self.verticalSlider, 0, 1, 1, 1)

        self.horizontalSlider = QtWidgets.QSlider(self.widget)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.gridLayout.addWidget(self.horizontalSlider, 1, 0, 1, 1)
                
        # Initialization of file name, canvas (on which signal is plotted: here the app window),
        # data frame and navigation toolbar
        self.file_name = ''
        self.graphicsView = PlotWidget(self.centralwidget)
        self.gridLayout.addWidget(self.graphicsView, 0, 0, 1, 1) 
        self.graphicsView.setObjectName("graphicsView")
        # Setting background in black
        self.graphicsView.setBackground((0, 0, 0))
        # Initial beginning & end values of x and y when graph first appears (should be accustomed to size of widget by trial)
        self.graphicsView.setRange(xRange=(0, 5), yRange=(0, 11), padding=0)
        # Showing grid with opacity = 0.5
        self.graphicsView.showGrid(x=True, y=True, alpha=0.5)
        # Setting panning and zooming limits by mouse movements
        self.graphicsView.setLimits(xMin=0, xMax=35, yMin=0, yMax=15, minXRange=0.5, maxXRange=15, minYRange=0.5, maxYRange=15)


        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Open File"))

    def openFile(self):
        # Getting the address of the csv file location and reading the data file
        # As it turns a tuple of file address and extenstion, we take te first item only (file name)
        self.file_name = QtWidgets.QFileDialog.getOpenFileName(caption="Choose Signal", directory="", filter="csv (*.csv)")[0]
        # Loading csv file into pandas data frame
        self.data_frame = pd.read_csv(self.file_name, encoding = 'utf-8').fillna(0)
        # Turning dataframe colmns into numpy arrays
        self.timeReadings = self.data_frame.iloc[:,0].to_numpy()
        self.signalReadings = self.data_frame.iloc[:,1].to_numpy()
        # PLotting with font size = 1.5 in blue color
        self.graphicsView.plot(self.timeReadings, self.signalReadings, pen=pyqtgraph.mkPen('b', width=1.5))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
