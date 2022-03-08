
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph
from pyqtgraph import PlotWidget
import pandas as pd
from sqlalchemy import false, true
from gui import Ui_MainWindow
import matplotlib.pyplot as plt 
import numpy as np 
from scipy import signal
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QWidget

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
        ###############
        self.setMaximumSliderValue = 100
        self.setMinimumSliderValue = 0
        self.colorPaletteSpectrogram = 'plasma'
        self.currentSpectrogram = 0

        self.file_name = ''

        
        self.ui.spectrogramMinimumPixelsIntenstiyHorizontalSlider.setValue(0)
        self.ui.spectrogramMaximumPixelsIntenstiyHorizontalSlider.setMinimum(0)
        self.ui.spectrogramMinimumPixelsIntenstiyHorizontalSlider.setMinimum(0)
        # Links of GUI Elements to Methods:
        self.ui.spectrogramChannelSelectionComboBox.currentIndexChanged.connect(lambda: self.chooseChannelToPlotSpectrogram(self.ui.spectrogramChannelSelectionComboBox.currentIndex()))
        self.ui.spectrogramPaletteSelectionComboBox.currentIndexChanged.connect(lambda: self.changeColorPaletteSpectrogram(self.ui.spectrogramPaletteSelectionComboBox.currentIndex()))
        self.ui.spectrogramMaximumPixelsIntenstiyHorizontalSlider.valueChanged.connect(lambda: self.contrastSpectrogram())
        self.ui.spectrogramMinimumPixelsIntenstiyHorizontalSlider.valueChanged.connect(lambda: self.contrastSpectrogram())
        
        

        self.ui.signalPlayPushButton.clicked.connect(self.openFile)
        self.figure = plt.figure(figsize=(15,5))
        self.Canvas = FigureCanvas(self.figure)
    # Methods
    def openFile(self):
        # Getting the address of the csv file location and reading the data file
        # As it turns a tuple of file address and extenstion, we take te first item only (file name)
        self.file_name = QtWidgets.QFileDialog.getOpenFileName(caption="Choose Signal", directory="", filter="csv (*.csv)")[0]
        # Loading csv file into pandas data frame
        self.data_frame = pd.read_csv(self.file_name, encoding = 'utf-8').fillna(0)
        # Turning dataframe colmns into numpy arrays
        self.channel1TimeReadings = self.data_frame.iloc[:,0].to_numpy()
        self.channel1AmplitudeReadings = self.data_frame.iloc[:,1].to_numpy()
        self.isChannel1Open = true
        # PLotting with font size = 1.5 in blue color
        self.ui.channelsGraphicsView.plot(self.channel1TimeReadings, self.channel1AmplitudeReadings, pen=pyqtgraph.mkPen('b', width=1.5))
    # function to plot spectrogram need time amplitude 
    def plotSpectrogram(self, time, amplitude):
        fs = 1/(time[1] - time [0])
        self.setMaximumSliderValue = fs/2
        self.ui.spectrogramMaximumPixelsIntenstiyHorizontalSlider.setMaximum(self.setMaximumSliderValue)
        self.ui.spectrogramMinimumPixelsIntenstiyHorizontalSlider.setMaximum(self.setMaximumSliderValue)
        self.ui.spectrogramMaximumPixelsIntenstiyHorizontalSlider.setValue(self.setMaximumSliderValue)
        self.freq, self.time, self.Sxx = signal.spectrogram(amplitude, fs)
        plt.pcolormesh(self.time, self.freq, 10*np.log10(self.Sxx), shading='auto', cmap= self.colorPaletteSpectrogram)
        plt.draw()
        plt.xlabel('time (sec)')
        #plt.yscale("log")
        plt.ylabel('frequency (Hz)')
        self.Canvas.draw()


    #! PLOT AND CLEAR SPECTROGRAMMMMMM
    # Function to clear spectrogram graph
    def clearSpectrogramGraph(self):
        self.figure = plt.figure(figsize=(15,5))
        self.Canvas = FigureCanvas(self.figure)
        self.ui.spectrogramGridLayout.addWidget(self.Canvas,0, 0, 1, 1)

    # To plot spectrogram from comboBox
    def chooseChannelToPlotSpectrogram (self,channelIndex):
        if channelIndex == 0:
            return
        if channelIndex == 1 and self.isChannel1Open == true:
            self.plotSpectrogram(self.channel1TimeReadings, self.channel1AmplitudeReadings)
            self.currentSpectrogram = 1
        elif channelIndex == 1 and self.isChannel1Open == False:
            self.clearSpectrogramGraph()
        elif channelIndex == 2 and self.isChannel2Open == true:
            self.plotSpectrogram(self.channel2TimeReadings, self.channel2AmplitudeReadings)
            self.currentSpectrogram = 2
        elif channelIndex == 2 and self.isChannel2Open == False:
            self.clearSpectrogramGraph()
        elif channelIndex == 3 and self.isChannel3Open == true:
            self.plotSpectrogram(self.channel3TimeReadings, self.channel3AmplitudeReadings)
            self.currentSpectrogram = 3
        elif channelIndex == 3 and self.isChannel3Open == False:
            self.clearSpectrogramGraph()

    #color palette function 
    def changeColorPaletteSpectrogram(self, colorIndex):
        print(colorIndex)
        if self.currentSpectrogram == 0:
            return
        if colorIndex == 0:
            self.colorPaletteSpectrogram = 'plasma'
        elif colorIndex == 1:
            self.colorPaletteSpectrogram = 'terrain'
        elif colorIndex == 2:
            self.colorPaletteSpectrogram = 'nipy_spectral'
        elif colorIndex == 3:
            self.colorPaletteSpectrogram = 'viridis'
        elif colorIndex == 4:
            self.colorPaletteSpectrogram = 'ocean'

        if self.currentSpectrogram == 1:
            self.plotSpectrogram(self.channel1TimeReadings, self.channel1AmplitudeReadings)
        elif self.currentSpectrogram == 2:
            self.plotSpectrogram(self.channel2TimeReadings, self.channel2AmplitudeReadings)
        elif self.currentSpectrogram == 3:
            self.plotSpectrogram(self.channel2TimeReadings, self.channel2AmplitudeReadings)
    # contrast spectrogram function
    def contrastSpectrogram(self):
        
        self.ui.spectrogramGridLayout.addWidget(self.Canvas,0, 0, 1, 1)
        
        if self.currentSpectrogram == 0:
            return

        self.minimumSliderValues = self.ui.spectrogramMinimumPixelsIntenstiyHorizontalSlider.value()
        self.maximumSliderValues = self.ui.spectrogramMaximumPixelsIntenstiyHorizontalSlider.value()

        print(self.minimumSliderValues)
        print(self.maximumSliderValues) 
        
        if self.minimumSliderValues > self.maximumSliderValues:
            self.minimumSliderValues = self.setMinimumSliderValue
        elif self.maximumSliderValues < self.minimumSliderValues:
            self.maximumSliderValues = self.setMaximumSliderValue
        elif self.minimumSliderValues == self.maximumSliderValues:
            return
        
        if self.currentSpectrogram == 1:
            self.fs = 1/(self.channel1TimeReadings[1] - self.channel1TimeReadings [0])
            self.freq, self.time, self.Sxx = signal.spectrogram(self.channel1AmplitudeReadings, self.fs)
            self.freqRange = np.where((self.freq >= self.minimumSliderValues) & (self.freq <= self.maximumSliderValues))
            self.freq = self.freq[self.freqRange]
            self.Sxx = self.Sxx[self.freqRange,:][0]
            plt.pcolormesh(self.time, self.freq, 10*np.log10(self.Sxx), shading='auto', cmap= self.colorPaletteSpectrogram)
        elif self.currentSpectrogram == 2:
            self.fs = 1/(self.channel2TimeReadings[1] - self.channel2TimeReadings [0])
            self.freq, self.time, self.Sxx = signal.spectrogram(self.channel2AmplitudeReadings, self.fs)
            self.freqRange = np.where((self.freq >= self.minimumSliderValues) & (self.freq <= self.maximumSliderValues))
            self.freq = self.freq[self.freqRange]
            self.Sxx = self.Sxx[self.freqRange,:][0]
            plt.pcolormesh(self.time, self.freq, 10*np.log10(self.Sxx), shading='auto', cmap= self.colorPaletteSpectrogram)
        elif self.currentSpectrogram == 3:
            self.fs = 1/(self.channel3TimeReadings[1] - self.channel3TimeReadings [0])
            self.freq, self.time, self.Sxx = signal.spectrogram(self.channel3AmplitudeReadings, self.fs)
            self.freqRange = np.where((self.freq >= self.minimumSliderValues) & (self.freq <= self.maximumSliderValues))
            self.freq = self.freq[self.freqRange]
            self.Sxx = self.Sxx[self.freqRange,:][0]
            plt.pcolormesh(self.time, self.freq, 10*np.log10(self.Sxx), shading='auto', cmap= self.colorPaletteSpectrogram)
        self.Canvas.draw()            




if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())