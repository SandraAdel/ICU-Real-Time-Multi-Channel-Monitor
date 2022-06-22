from copy import copy
import sys
import math
import shutil
import os
import csv
import datetime
import numpy as np
import pandas as pd
import pyqtgraph.exporters
import pyqtgraph as pg
from PyQt5 import QtWidgets as QtWidgets
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5.QtWidgets import QApplication, QMainWindow
from gui import Ui_MainWindow
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy import signal
import statistics
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import matplotlib.backends.backend_pdf
from PyPDF2 import PdfFileMerger
import sys
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
#from PyQt5.QtCoree import*

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.channel1Signal = pg.PlotCurveItem()
        self.channel1TimeReadings = [0,0]
        self.channel1AmplitudeReadings = [0,0]
        self.channel1PlottedXCoordinates = []
        self.channel1PlottedYCoordinates = []
        self.channel2Signal = pg.PlotCurveItem()
        self.channel2TimeReadings = [0,0]
        self.channel2AmplitudeReadings = [0,0]
        self.channel2PlottedXCoordinates = []
        self.channel2PlottedYCoordinates = []
        self.channel3Signal = pg.PlotCurveItem()
        self.channel3TimeReadings = [0,0]
        self.channel3AmplitudeReadings = [0,0]
        self.channel3PlottedXCoordinates = []
        self.channel3PlottedYCoordinates = []
        self.isChannel1Open, self.isChannel2Open, self.isChannel3Open = False, False, False
        self.isChannel1Shown, self.isChannel2Shown, self.isChannel3Shown = False, False, False
        self.counter=0
        self.newChannelStart=0
        self.xrange=1
        self.xrangeupdated=0
        self.speedIncrement=0
        self.currentChannelNumber= None
        self.timer= self.ui.timer
        self.setMaximumSliderValue = 100
        self.setMinimumSliderValue = 0
        self.colorPaletteSpectrogram = 'plasma'
        self.currentSpectrogram = 0
        self.selectedColor1 ='b'
        self.signalWidth1 = 1.5
        self.selectedColor2 ='r'
        self.signalWidth2 = 1.5
        self.selectedColor3 ='g'
        self.signalWidth3 = 1.5
        #self.pointsToAppend = [0, 0, 0]
        self.pen = pg.mkPen(color=(255, 0, 0), width=1)
        self.graphChannels = self.ui.channelsGraphicsView

        self.automaticView, self.manualView, self.playModefirstTimeAutomaticToManualTransition, self.pauseModefirstTimeAutomaticToManualTransition = True, False, True, True
        self.minimumVisibleX, self.maximumVisibleX, self.minimumVisibleY, self.maximumVisibleY = 0, 5, 0, 2 
        self.ui.channelsGraphicsView.setRange(xRange=(self.minimumVisibleX, self.maximumVisibleX), yRange=(self.minimumVisibleY, self.maximumVisibleY), padding=0)
        self.minimumX, self.maximumX, self.minimumY, self.maximumY, self.minimumXRange, self.minimumYRange = 0, 5, 0, 4, 2, 2
        self.ui.channelsGraphicsView.setLimits(xMin=self.minimumX, xMax=self.maximumX, yMin=self.minimumY, yMax=self.maximumY, minXRange=self.minimumXRange, maxXRange=(self.maximumX-self.minimumX), minYRange=self.minimumYRange, maxYRange=(self.maximumY-self.minimumY))
        self.ui.signalScrollHorizontalSlider.setMinimum(self.minimumX)
        self.ui.signalScrollHorizontalSlider.setMaximum(self.maximumX)
        self.ui.signalScrollVerticalSlider.setMinimum(self.minimumX)
        self.ui.signalScrollVerticalSlider.setMaximum(self.maximumY)
        self.EnableManualViewControls(False)
        self.pauseModeTimer= qtc.QTimer()
        self.pauseModeTimer.setInterval(50)
        self.pauseModeTimer.timeout.connect(self.pauseModeAutomtaicOrManualViewCheck)

        # Links of Methods to GUI Elements
        self.ui.openChannel1Action.triggered.connect(lambda: self.open(1))
        self.ui.openChannel2Action.triggered.connect(lambda: self.open(2))
        self.ui.openChannel3Action.triggered.connect(lambda: self.open(3))
        self.ui.signalPlayPushButton.clicked.connect(self.play)
        self.ui.signalPausePushButton.clicked.connect(self.pause)
        self.ui.signalSpeedupPushButton.clicked.connect(self.signalspeedup)
        self.ui.signalSpeedDownPushButton.clicked.connect(self.signalspeeddown)
        self.ui.spectrogramMinimumPixelsIntenstiyHorizontalSlider.setValue(0)
        self.ui.spectrogramMaximumPixelsIntenstiyHorizontalSlider.setMinimum(0)
        self.ui.spectrogramMinimumPixelsIntenstiyHorizontalSlider.setMinimum(0)

        self.ui.spectrogramChannelSelectionComboBox.currentIndexChanged.connect(lambda: self.chooseChannelToPlotSpectrogram(self.ui.spectrogramChannelSelectionComboBox.currentIndex()))
        self.ui.spectrogramPaletteSelectionComboBox.currentIndexChanged.connect(lambda: self.changeColorPaletteSpectrogram(self.ui.spectrogramPaletteSelectionComboBox.currentIndex()))
        self.ui.spectrogramMaximumPixelsIntenstiyHorizontalSlider.valueChanged.connect(lambda: self.contrastSpectrogram())
        self.ui.spectrogramMinimumPixelsIntenstiyHorizontalSlider.valueChanged.connect(lambda: self.contrastSpectrogram())
        self.ui.saveAsPdfAction.triggered.connect(lambda: self.tableCreation())

        # self.ui.channel1ChangeColorAction.triggered.connect(lambda: self.openColorWindow(1))
        # self.ui.channel2ChangeColorAction.triggered.connect(lambda: self.openColorWindow(2))
        # self.ui.channel3ChangeColorAction.triggered.connect(lambda: self.openColorWindow(3))
        self.ui.channelsSpectrogramLabelEditingComboBox.currentIndexChanged.connect(lambda: self.editLabel(self.ui.channelsSpectrogramLabelEditingComboBox.currentIndex()))
        #! set ture when ro'aa open the signal
        self.ui.channel1ShowHideCheckBox.setChecked(True)
        self.ui.channel2ShowHideCheckBox.setChecked(True)
        self.ui.channel3ShowHideCheckBox.setChecked(True)
        self.ui.channel1ShowHideCheckBox.stateChanged.connect(lambda: self.showHide(1))
        self.ui.channel2ShowHideCheckBox.stateChanged.connect(lambda: self.showHide(2))
        self.ui.channel3ShowHideCheckBox.stateChanged.connect(lambda: self.showHide(3))
        self.ui.channel1ChangeColorAction.triggered.connect(lambda: self.openColorWindow(1))
        self.ui.channel2ChangeColorAction.triggered.connect(lambda: self.openColorWindow(2))
        self.ui.channel3ChangeColorAction.triggered.connect(lambda: self.openColorWindow(3))
        self.figure = plt.figure(figsize=(15,5))
        self.Canvas = FigureCanvas(self.figure)

        self.ui.signalScrollHorizontalSlider.valueChanged.connect(self.HorizontalScroll)
        self.ui.signalScrollVerticalSlider.valueChanged.connect(self.VerticalScroll)
        self.ui.signalZoomInPushButton.clicked.connect(self.ZoomIn)
        self.ui.signalZoomOutPushButton.clicked.connect(self.ZoomOut)
        self.ui.automaticViewButton.clicked.connect(lambda: self.AutomaticOrManualViewSelection('Automatic'))
        self.ui.manualViewButton.clicked.connect(lambda: self.AutomaticOrManualViewSelection('Manual'))

    # Methods

    def open(self, channelNumber):

        self.timer.stop()
        self.currentChannelNumber=channelNumber
        self.filename = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Load Signal', './', "(*.csv *.xls *.txt)")[0]
        self.data_frame = pd.read_csv(self.filename, encoding = 'utf-8').fillna(0)
        
        if self.currentChannelNumber==1:
            self.channel1TimeReadings = self.data_frame.iloc[:,0].to_numpy()
            self.channel1AmplitudeReadings = self.data_frame.iloc[:,1].to_numpy()
            self.isChannel1Open=True
            self.isChannel1Shown=True
            self.ui.channel1ShowHideCheckBox.setChecked(True)
        elif self.currentChannelNumber==2:
            self.channel2TimeReadings = self.data_frame.iloc[:,0].to_numpy() + self.newChannelStart
            self.channel2AmplitudeReadings = self.data_frame.iloc[:,1].to_numpy()
            self.isChannel2Open=True
            self.isChannel2Shown=True
            self.ui.channel2ShowHideCheckBox.setChecked(True)
        elif self.currentChannelNumber==3:
            self.channel3TimeReadings = self.data_frame.iloc[:,0].to_numpy() + self.newChannelStart
            self.channel3AmplitudeReadings = self.data_frame.iloc[:,1].to_numpy()
            self.isChannel3Open=True
            self.isChannel3Shown=True
            self.ui.channel3ShowHideCheckBox.setChecked(True)
        
        '''
        self.channel1TimeReadings = np.array(self.channel1TimeReadings)
        self.channel1AmplitudeReadings = np.array(self.channel1AmplitudeReadings)
        if self.currentChannelNumber == 2:
            self.channel2TimeReadings = np.array(self.channel2TimeReadings)
            self.channel2AmplitudeReadings = np.array(self.channel2AmplitudeReadings)
        if self.currentChannelNumber == 3:   
            self.channel3TimeReadings = np.array(self.channel3TimeReadings)
            self.channel3AmplitudeReadings = np.array(self.channel3AmplitudeReadings)    
        '''
        self.play()
        #self.timer.timeout.connect(self.updatePlot)

    def play(self):
        self.pauseModeTimer.stop()
        self.timer.start()
        self.timer.timeout.connect(self.updatePlot)

    def pause(self):
        self.timer.stop()
        self.pauseModeTimer.start()

    def updatePlot(self):

        #self.graphChannels.clear()
        if self.isChannel1Open :
            self.channel1PlottedXCoordinates=self.channel1TimeReadings[0:self.counter+1]
            self.channel1PlottedYCoordinates=self.channel1AmplitudeReadings[0:self.counter+1]
            self.increment=self.channel1TimeReadings[1]-self.channel1TimeReadings[0]
            #self.increment=0.1
            ########### Adjusting view ##############
            self.PlayModeAutomtaicOrManualViewCheck()
            #########################################
            self.channel1Signal.setData(self.channel1PlottedXCoordinates,  self.channel1PlottedYCoordinates, pen=pg.mkPen(self.selectedColor1, width=self.signalWidth1 ))
            self.graphChannels.addItem(self.channel1Signal)
            #self.Item.setData(self.xplotted,  self.yplotted, pen=pg.mkPen('r', width=1.5))
            #self.graphChannels.addItem(self.Item)
            yminimum=np.min(self.channel1AmplitudeReadings)
            ymaximum=np.max(self.channel1AmplitudeReadings)
            ####self.graphChannels.setYRange(yminimum, ymaximum)
            if self.counter == 0 :
                pass
                ####self.graphChannels.setXRange( 0  , self.xrange, padding=0 )
            elif self.counter >= (1/self.increment)  :
                ####self.graphChannels.setXRange( self.xrangeupdated  , self.xrange, padding=0)
                self.xrange = self.xrange + self.increment +self.increment*self.speedIncrement
                self.xrangeupdated = self.xrangeupdated +self.increment +self.increment*self.speedIncrement
            self.newChannelStart=self.channel1TimeReadings[self.counter]
            self.counter +=(self.speedIncrement+1)
            if self.isChannel2Open:
                if np.min(self.channel1AmplitudeReadings) >np.min(self.channel2AmplitudeReadings):
                    yminimum=np.min(self.channel2AmplitudeReadings)
                if np.max(self.channel1AmplitudeReadings) <np.max(self.channel2AmplitudeReadings):
                    ymaximum=np.max(self.channel2AmplitudeReadings)
                
                ####self.graphChannels.setYRange(yminimum, ymaximum)
                self.channel2PlottedXCoordinates=self.channel2TimeReadings[0:self.counter+1]
                self.channel2PlottedYCoordinates=self.channel2AmplitudeReadings[0:self.counter+1]
                #self.increment=self.time2[1]-self.time2[0]
                ########### Adjusting view ##############
                self.PlayModeAutomtaicOrManualViewCheck()
                #########################################
                self.channel2Signal.setData(self.channel2PlottedXCoordinates,  self.channel2PlottedYCoordinates, pen=pg.mkPen(self.selectedColor2, width=self.signalWidth2 ))
                self.graphChannels.addItem(self.channel2Signal)
                #self.Item.setData(self.xplotted,  self.yplotted, pen=pg.mkPen('r', width=1.5))
                #self.graphChannels.addItem(self.Item)

                #self.graphChannels.setYRange(np.min(self.amp2), np.max(self.amp2))
                if self.counter == 0 :
                    pass
                    ####self.graphChannels.setXRange( 0  , self.xrange, padding=0 )
                elif self.counter >= (1/self.increment)  :
                    ####self.graphChannels.setXRange( self.xrangeupdated  , self.xrange, padding=0)
                    self.xrange = self.xrange + self.increment +self.increment*self.speedIncrement
                    self.xrangeupdated = self.xrangeupdated +self.increment +self.increment*self.speedIncrement
                self.counter +=(self.speedIncrement+1)
                if self.isChannel3Open:
                    if np.min(self.channel3AmplitudeReadings) >np.min(self.channel3AmplitudeReadings):
                        yminimum=np.min(self.channel3AmplitudeReadings)
                    if np.max(self.channel3AmplitudeReadings) <np.max(self.channel3AmplitudeReadings):
                        ymaximum=np.max(self.channel3AmplitudeReadings)
                    
                    ####self.graphChannels.setYRange(yminimum, ymaximum)
                    self.channel3PlottedXCoordinates=self.channel3TimeReadings[0:self.counter+1]
                    self.channel3PlottedYCoordinates=self.channel3AmplitudeReadings[0:self.counter+1]
                    #self.increment=self.time2[1]-self.time2[0]
                    ########### Adjusting view ##############
                    self.PlayModeAutomtaicOrManualViewCheck()
                    #########################################
                    self.channel3Signal.setData(self.channel3PlottedXCoordinates,  self.channel3PlottedYCoordinates, pen=pg.mkPen(self.selectedColor3, width=self.signalWidth3 ))
                    self.graphChannels.addItem(self.channel3Signal)
                    #self.Item.setData(self.xplotted,  self.yplotted, pen=pg.mkPen('r', width=1.5))
                    #self.graphChannels.addItem(self.Item)

                    #self.graphChannels.setYRange(np.min(self.amp2), np.max(self.amp2))
                    if self.counter == 0 :
                        pass
                        ####self.graphChannels.setXRange( 0  , self.xrange, padding=0 )
                    elif self.counter >= (1/self.increment)  :
                        ####self.graphChannels.setXRange( self.xrangeupdated  , self.xrange, padding=0)
                        self.xrange = self.xrange + self.increment +self.increment*self.speedIncrement
                        self.xrangeupdated = self.xrangeupdated +self.increment +self.increment*self.speedIncrement
                    self.counter +=(self.speedIncrement+1)
        
        #When the signal file is finished, repeat it to visualize as if it is real time data
        # TO DO: complete it
        # if self.counter > len(self.time[self.channelNumber]):
        #     self.timer.stop()
        #     self.counter= 0
        #     # self.xrange = 1
        #     # self.xrangeupdated= 0

    
    def signalspeedup(self):
        self.speedIncrement +=1

    def signalspeeddown(self):
        #to ensure that the speed is not negative
        if self.speedIncrement>0:
            self.speedIncrement -=1
        else:
            self.speedIncrement=0

    def AutomaticOrManualViewSelection(self, mode):
        if mode == 'Automatic':
            self.automaticView = True
            self.manualView = False
        elif mode == 'Manual':
            self.automaticView = False
            self.manualView = True

    def CheckIfAllChannelsAreClosedOrHidden(self):
        if self.isChannel1Open and self.isChannel1Shown:
            nextXCoordinateToPlot = self.channel1PlottedXCoordinates[-1]
        elif self.isChannel2Open and self.isChannel2Shown:
            nextXCoordinateToPlot = self.channel2PlottedXCoordinates[-1]
        elif self.isChannel3Open and self.isChannel3Shown:
            nextXCoordinateToPlot = self.channel3PlottedXCoordinates[-1]
        else:
            nextXCoordinateToPlot = None
        return nextXCoordinateToPlot

    def UpdateAutomaticView(self):
        self.EnableManualViewControls(False)
        self.UpdateCurrentVisibleAxis()
        VisibleYCoordinates = []
        nextXCoordinateToPlot = self.CheckIfAllChannelsAreClosedOrHidden()
        if  nextXCoordinateToPlot == None: return
        if nextXCoordinateToPlot <= self.maximumVisibleX:
            if self.isChannel1Open and self.isChannel1Shown:
                VisibleYCoordinates.extend(self.channel1PlottedYCoordinates)
            if self.isChannel2Open and self.isChannel2Shown:
                VisibleYCoordinates.extend(self.channel2PlottedYCoordinates)
            if self.isChannel3Open and self.isChannel3Shown:
                VisibleYCoordinates.extend(self.channel3PlottedYCoordinates)
        elif nextXCoordinateToPlot > self.maximumVisibleX:
            VisibleXRangeBeforeUpdate = self.maximumVisibleX - self.minimumVisibleX
            self.maximumVisibleX = round(nextXCoordinateToPlot, 3) 
            self.minimumVisibleX = round(self.maximumVisibleX - VisibleXRangeBeforeUpdate, 3)
            if self.isChannel1Open and self.isChannel1Shown and list(self.channel1PlottedXCoordinates):
                FirstVisibleXCoordinateIndex = findIndexOfNearestValue(self.channel1PlottedXCoordinates, round(nextXCoordinateToPlot-VisibleXRangeBeforeUpdate, 3))
                VisibleYCoordinates.extend(self.channel1PlottedYCoordinates[FirstVisibleXCoordinateIndex:])
            if self.isChannel2Open and self.isChannel2Shown and list(self.channel2PlottedXCoordinates):
                FirstVisibleXCoordinateIndex = findIndexOfNearestValue(self.channel2PlottedXCoordinates, round(nextXCoordinateToPlot-VisibleXRangeBeforeUpdate, 3))
                VisibleYCoordinates.extend(self.channel2PlottedYCoordinates[FirstVisibleXCoordinateIndex:])
            if self.isChannel3Open and self.isChannel3Shown and list(self.channel3PlottedXCoordinates):
                FirstVisibleXCoordinateIndex = findIndexOfNearestValue(self.channel3PlottedXCoordinates, round(nextXCoordinateToPlot-VisibleXRangeBeforeUpdate, 3))
                VisibleYCoordinates.extend(self.channel3PlottedYCoordinates[FirstVisibleXCoordinateIndex:])
            #print('FirstVisibleXCoordinateIndex', FirstVisibleXCoordinateIndex)
            #print(len(VisibleYCoordinates))
        self.maximumX = self.maximumVisibleX
        minimumVisibleAmplitude, maximumVisibleAmplitude = min(VisibleYCoordinates) - 0.1, max(VisibleYCoordinates) + 0.1
        self.minimumY, self.maximumY = round(minimumVisibleAmplitude, 3), round(maximumVisibleAmplitude, 3)
        self.ui.channelsGraphicsView.setLimits(xMin=self.minimumVisibleX, xMax=self.maximumVisibleX, yMin=self.minimumY, yMax=self.maximumY, minXRange=self.minimumXRange, maxXRange=(self.maximumX-self.minimumX), minYRange=(self.maximumY-self.minimumY), maxYRange=(self.maximumY-self.minimumY))
        self.ui.channelsGraphicsView.setXRange(self.minimumVisibleX, self.maximumVisibleX, padding=0)
        self.ui.channelsGraphicsView.setYRange(self.minimumY, self.maximumY, padding=0)

    def UpdateManualView(self, firstTimeAutomaticToManualTransition):
        nextXCoordinateToPlot = self.CheckIfAllChannelsAreClosedOrHidden()
        if  nextXCoordinateToPlot == None: self.EnableManualViewControls(False); return
        self.UpdateCurrentVisibleAxis()
        if nextXCoordinateToPlot > self.maximumVisibleX: self.maximumX = nextXCoordinateToPlot
        if firstTimeAutomaticToManualTransition:
            if (self.maximumVisibleY-self.minimumVisibleY) < self.minimumYRange:
                visibleAndMinimumYRangeDifference = (self.minimumYRange-(self.maximumVisibleY-self.minimumVisibleY))
                if (self.minimumVisibleY-(visibleAndMinimumYRangeDifference/2)) < 0:
                    self.maximumY = self.maximumVisibleY + round(visibleAndMinimumYRangeDifference-self.minimumVisibleY, 3)
                    self.minimumY = 0
                else:
                    self.minimumY = self.minimumVisibleY - round(visibleAndMinimumYRangeDifference/2, 3)
                    self.maximumY = self.maximumVisibleY + round(visibleAndMinimumYRangeDifference/2, 3)
            else:
                self.minimumY = self.minimumVisibleY
                self.maximumY = self.maximumVisibleY
        self.ui.channelsGraphicsView.setLimits(xMin=self.minimumX, xMax=self.maximumX, yMin=self.minimumY, yMax=self.maximumY, minXRange=self.minimumXRange, maxXRange=(self.maximumVisibleX-self.minimumX), minYRange=self.minimumYRange, maxYRange=(self.maximumY-self.minimumY))
        if firstTimeAutomaticToManualTransition: self.ui.channelsGraphicsView.setYRange(self.minimumY , self.maximumY, padding=0)
        self.UpdateSlidersLimit()
        if firstTimeAutomaticToManualTransition: self.UpdateSlidersValue()
        self.EnableManualViewControls(True)

    def PlayModeAutomaticViewAdjust(self):
        self.UpdateAutomaticView()
        self.playModefirstTimeAutomaticToManualTransition = True

    def PlayModeManualViewAdjust(self):
        self.UpdateManualView(self.playModefirstTimeAutomaticToManualTransition)
        self.playModefirstTimeAutomaticToManualTransition = False

    def PauseModeAutomaticViewAdjust(self):
        self.UpdateAutomaticView()
        self.pauseModefirstTimeAutomaticToManualTransition = True

    def PauseModeManualViewAdjust(self):
        self.UpdateManualView(self.pauseModefirstTimeAutomaticToManualTransition)
        self.pauseModefirstTimeAutomaticToManualTransition = False

    def pauseModeAutomtaicOrManualViewCheck(self):
        if self.automaticView: self.PauseModeAutomaticViewAdjust()
        elif self.manualView: self.PauseModeManualViewAdjust()

    def PlayModeAutomtaicOrManualViewCheck(self):
        if self.automaticView: self.PlayModeAutomaticViewAdjust()
        elif self.manualView: self.PlayModeManualViewAdjust()  

    def HorizontalScroll(self, sliderValue):
        self.UpdateCurrentVisibleAxis()
        scrollFactor = ( self.maximumX - (self.maximumVisibleX - self.minimumVisibleX) ) / ( self.maximumX - self.minimumX )
        scrollStep = scrollFactor * sliderValue
        self.maximumVisibleX = round((self.maximumVisibleX - self.minimumVisibleX) + scrollStep, 3)
        self.minimumVisibleX = round(0 + scrollStep, 3)
        self.ui.channelsGraphicsView.setXRange(self.minimumVisibleX, self.maximumVisibleX, padding=0)

    def VerticalScroll(self, sliderValue):
        self.UpdateCurrentVisibleAxis()
        scrollFactor = ( (self.maximumY - self.maximumVisibleY) + (self.minimumVisibleY - self.minimumY) ) / ( self.maximumY - self.minimumY )
        scrollStep = scrollFactor * sliderValue
        self.maximumVisibleY = round((self.maximumVisibleY - self.minimumVisibleY) + scrollStep, 3)
        self.minimumVisibleY = round(0 + scrollStep, 3)
        self.ui.channelsGraphicsView.setYRange(self.minimumVisibleY, self.maximumVisibleY, padding=0)

    def ZoomIn(self):
        #visibleAreaToMaximumAreaRatio = ( (self.maximumVisibleX - self.minimumVisibleX) * (self.maximumVisibleY - self.minimumVisibleY) ) / ( (self.maximumX - self.minimumX) * (self.maximumY - self.minimumY) )
        #zoomFactor = round(visibleAreaToMaximumAreaRatio * ( (self.maximumVisibleX - self.minimumVisibleX) * (self.maximumVisibleY - self.minimumVisibleY) ), 2)
        self.UpdateCurrentVisibleAxis()
        zoomFactor = 0.25
        self.minimumVisibleX, self.maximumVisibleX = AdjustAxesWithZoomFactor('ZoomIn', None, 2*zoomFactor, None, None, self.minimumVisibleX, self.maximumVisibleX, self.minimumXRange)
        self.minimumVisibleY, self.maximumVisibleY = AdjustAxesWithZoomFactor('ZoomIn', None, zoomFactor, None, None, self.minimumVisibleY, self.maximumVisibleY, self.minimumYRange)
        self.ui.channelsGraphicsView.setRange(xRange=(self.minimumVisibleX, self.maximumVisibleX), yRange=(self.minimumVisibleY, self.maximumVisibleY), padding=0)
        self.UpdateSlidersValue()

    def ZoomOut(self):
        #visibleAreaToMaximumAreaRatio = ( (self.maximumVisibleX - self.minimumVisibleX) * (self.maximumVisibleY - self.minimumVisibleY) ) / ( (self.maximumX - self.minimumX) * (self.maximumY - self.minimumY) )
        #zoomFactor = visibleAreaToMaximumAreaRatio * ( (self.maximumVisibleX - self.minimumVisibleX) * (self.maximumVisibleY - self.minimumVisibleY) )
        self.UpdateCurrentVisibleAxis()
        zoomFactor = 0.25
        self.minimumVisibleX = AdjustAxesWithZoomFactor('ZoomOut', self.minimumVisibleX, 2*zoomFactor, self.minimumX, 'Decrement', None, None, None)
        self.maximumVisibleX = AdjustAxesWithZoomFactor('ZoomOut', self.maximumVisibleX, 2*zoomFactor, self.maximumX, 'Increment', None, None, None)
        self.minimumVisibleY = AdjustAxesWithZoomFactor('ZoomOut', self.minimumVisibleY, zoomFactor, self.minimumY, 'Decrement', None, None, None)
        self.maximumVisibleY = AdjustAxesWithZoomFactor('ZoomOut', self.maximumVisibleY, zoomFactor, self.maximumY, 'Increment', None, None, None)
        self.ui.channelsGraphicsView.setRange(xRange=(self.minimumVisibleX, self.maximumVisibleX), yRange=(self.minimumVisibleY, self.maximumVisibleY), padding=0)
        self.UpdateSlidersValue()

    def UpdateSlidersLimit(self):
        self.ui.signalScrollHorizontalSlider.setMinimum(self.minimumX)
        self.ui.signalScrollHorizontalSlider.setMaximum(math.ceil(self.maximumX))
        self.ui.signalScrollVerticalSlider.setMinimum(math.floor(self.minimumY))
        self.ui.signalScrollVerticalSlider.setMaximum(math.ceil(self.maximumY))

    def UpdateSlidersValue(self):
        self.UpdateCurrentVisibleAxis()
        horizontalScrollFactor = ( self.maximumX - (self.maximumVisibleX - self.minimumVisibleX) ) / ( self.maximumX - self.minimumX )
        verticalScrollFactor = round(( (round(self.maximumY, 3) - round(self.maximumVisibleY, 3)) + (round(self.minimumVisibleY, 3) - round(self.minimumY, 3)) ) / ( round(self.maximumY, 3) - round(self.minimumY, 3) ), 3)
        if horizontalScrollFactor != 0:
            horizontalSliderValue = math.ceil(self.minimumVisibleX/horizontalScrollFactor)
            self.ui.signalScrollHorizontalSlider.setValue(horizontalSliderValue)
        if verticalScrollFactor != 0:
            verticalSliderValue = round(self.minimumVisibleY/verticalScrollFactor)
            self.ui.signalScrollVerticalSlider.setValue(verticalSliderValue)

    def EnableManualViewControls(self, condition):
        self.ui.signalScrollHorizontalSlider.setEnabled(condition)
        self.ui.signalScrollVerticalSlider.setEnabled(condition)
        self.ui.signalZoomInPushButton.setEnabled(condition)
        self.ui.signalZoomOutPushButton.setEnabled(condition)
        self.ui.channelsGraphicsView.setMouseEnabled(x=condition, y=condition)

    def UpdateCurrentVisibleAxis(self):
        [[self.minimumVisibleX, self.maximumVisibleX], [self.minimumVisibleY, self.maximumVisibleY]] = self.ui.channelsGraphicsView.viewRange()      


    def plotSpectrogram(self, time, amplitude):
        # self.figure = plt.figure(figsize=(15,5))
        # self.Canvas = FigureCanvas(self.figure)
        # self.ui.spectrogramGridLayout.addWidget(self.Canvas,0, 0, 1, 1)
        self.clearSpectrogramGraph()
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

    def clearSpectrogramGraph(self):
        self.figure = plt.figure(figsize=(15,5))
        self.Canvas = FigureCanvas(self.figure)
        self.ui.spectrogramGridLayout.addWidget(self.Canvas,0, 0, 1, 1)

    # To plot spectrogram from comboBox
    def chooseChannelToPlotSpectrogram (self,channelIndex):
        if channelIndex == 0:
            return
        if channelIndex == 1 and self.isChannel1Open ==  True:
            #print("1")
            self.plotSpectrogram(self.channel1TimeReadings, self.channel1AmplitudeReadings)
            self.currentSpectrogram = 1
            self.ui.spectrogramLabel.setText(self.ui.channel1Label.text())
        elif channelIndex == 1 and self.isChannel1Open == False:
            self.clearSpectrogramGraph()
        elif channelIndex == 2 and self.isChannel2Open == True:
            self.plotSpectrogram(self.channel2TimeReadings, self.channel2AmplitudeReadings)
            self.currentSpectrogram = 2
            self.ui.spectrogramLabel.setText(self.ui.channel2Label.text())
        elif channelIndex == 2 and self.isChannel2Open == False:
            self.clearSpectrogramGraph()
        elif channelIndex == 3 and self.isChannel3Open == True:
            self.plotSpectrogram(self.channel3TimeReadings, self.channel3AmplitudeReadings)
            self.currentSpectrogram = 3
            self.ui.spectrogramLabel.setText(self.ui.channel3Label.text())
        elif channelIndex == 3 and self.isChannel3Open == False:
            self.clearSpectrogramGraph()

    # Color palette function 
    def changeColorPaletteSpectrogram(self, colorIndex):
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

     # Function to calculate some data statistics
    def calculateStatisticsData(self, time, amplitude):
        self.mean = statistics.mean(amplitude)
        self.standardDeviation = statistics.stdev(amplitude)
        self.maximumAmplitude = max(amplitude)
        self.minimumAmplitude = min(amplitude)
        self.duration = max(time)
        return self.mean, self.standardDeviation, self.maximumAmplitude, self.minimumAmplitude, self.duration

    # Function to creat a table
    def tableCreation(self):
        self.items = []
        self.document = SimpleDocTemplate("StatisticsData.pdf", pagesize=letter)
        self.channel1Mean, self.channel1standardDeviation, self.channel1maximumAmplitude, self.channel1minimumAmplitude, self.channel1duration = self.calculateStatisticsData(self.channel1TimeReadings, self.channel1AmplitudeReadings)
        self.channel2Mean, self.channel2standardDeviation, self.channel2maximumAmplitude, self.channel2minimumAmplitude, self.channel2duration = self.calculateStatisticsData(self.channel2TimeReadings, self.channel2AmplitudeReadings)
        self.channel3Mean, self.channel3standardDeviation, self.channel3maximumAmplitude, self.channel3minimumAmplitude, self.channel3duration = self.calculateStatisticsData(self.channel3TimeReadings, self.channel3AmplitudeReadings)
        
        # self.reportData = [['','Channel 1','Channel 2','Channel 3'],
        # ['Mean', self.channel1Mean, self.channel1Mean, self.channel1Mean],
        # ['Standard Deviation', self.channel1standardDeviation, self.channel1standardDeviation, self.channel1standardDeviation],
        # ['Maximum', self.channel1maximumAmplitude, self.channel1maximumAmplitude, self.channel1maximumAmplitude],
        # ['Minimum', self.channel1minimumAmplitude, self.channel1minimumAmplitude, self.channel1minimumAmplitude],
        # ['Duration', self.channel1duration, self.channel1duration, self.channel1duration]]

        self.reportData = [['','Channel 1','Channel 2','Channel 3'],
        ['Mean', self.channel1Mean, self.channel2Mean, self.channel3Mean],
        ['Standard Deviation', self.channel1standardDeviation, self.channel2standardDeviation, self.channel3standardDeviation],
        ['Maximum', self.channel1maximumAmplitude, self.channel2maximumAmplitude, self.channel3maximumAmplitude],
        ['Minimum', self.channel1minimumAmplitude, self.channel2minimumAmplitude, self.channel3minimumAmplitude],
        ['Duration', self.channel1duration, self.channel2duration, self.channel3duration]]

        self.table = Table(self.reportData, 4*[2*inch], 6*[0.5*inch])
        self.table.setStyle(TableStyle([('ALIGN', (1,1),(-2,-2),'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black)]))
        self.items.append(self.table)
        self.document.build(self.items)

    def openColorWindow(self, ChannelNo):

        if ChannelNo==1 :
                    self.selectedColor1= QColorDialog.getColor() 
                    self.channel1Signal.setPen(pg.mkPen(self.selectedColor1,width= self.signalWidth1 ))
              
                    
        if ChannelNo==2:
                    self.selectedColor2= QColorDialog.getColor() 
                    self.channel2Signal.setPen(pg.mkPen(self.selectedColor2,width= self.signalWidth2 ))
              
        if ChannelNo==3:
                    self.selectedColor3= QColorDialog.getColor() 
                    self.channel3Signal.setPen(pg.mkPen(self.selectedColor3,width= self.signalWidth3 ))
              

    def showHide(self, channelNo):

        if channelNo==1 :
            if self.isChannel1Open==True and self.ui.channel1ShowHideCheckBox.isChecked() :
                self.signalWidth1 = 1.5
                self.channel1Signal.setPen(pyqtgraph.mkPen(width= self.signalWidth1 ))
                self.isChannel1Shown==True
                self.ui.channel1Label.show()
            else:
                self.signalWidth1 = 0.001
                self.channel1Signal.setPen(pyqtgraph.mkPen(width= self.signalWidth1 ))
                self.isChannel1Shown==False
                self.ui.channel1Label.hide()

        if channelNo==2 :
          if self.isChannel2Open==True and self.ui.channel2ShowHideCheckBox.isChecked() :
                self.signalWidth2 = 1.5
                self.channel2Signal.setPen(pyqtgraph.mkPen(width= self.signalWidth2 ))
                self.isChannel2Shown==True
                self.ui.channel2Label.show()
          else:
                self.signalWidth2 = 0.001
                self.channel2Signal.setPen(pyqtgraph.mkPen(width= self.signalWidth2 ))
                self.isChannel2Shown==False
                self.ui.channel2Label.hide()
            
        if channelNo==3 :
          if self.isChannel3Open==True and self.ui.channel3ShowHideCheckBox.isChecked() :
                self.signalWidth3 = 1.5
                self.channel3Signal.setPen(pyqtgraph.mkPen(width= self.signalWidth3 ))
                self.isChannel3Shown==True
                self.ui.channel3Label.show()
          else:
                self.signalWidth3 = 0.001
                self.channel3Signal.setPen(pyqtgraph.mkPen(width= self.signalWidth3 ))
                self.isChannel3Shown==False 
                self.ui.channel3Label.hide()

    
    def editLabel(self, channelNo):
        if channelNo==1:
            self.ui.channel1Label.setText(self.ui.channelsSpectrogramLineEdit.text())
        elif channelNo==2:
            self.ui.channel2Label.setText(self.ui.channelsSpectrogramLineEdit.text())
        elif channelNo==3:
            self.ui.channel3Label.setText(self.ui.channelsSpectrogramLineEdit.text())
        if self.currentSpectrogram == 0:
            return
        if self.currentSpectrogram == 1:
            self.ui.spectrogramLabel.setText(self.ui.channel1Label.text())
        elif self.currentSpectrogram ==2:
            self.ui.spectrogramLabel.setText(self.ui.channel2Label.text())
        elif self.currentSpectrogram == 3:
            self.ui.spectrogramLabel.setText(self.ui.channel3Label.text())

# Helper function OUTSIDE CLASS
def AdjustAxesWithZoomFactor(zoomType, variableToAdjust, zoomFactor, variableLimit, changeType, variableMinimum, variableMaximum, variableRangeLimit):
    if zoomType == 'ZoomOut':
        if changeType == 'Decrement':
            variableToAdjust -= zoomFactor
            if (variableToAdjust < variableLimit): variableToAdjust = variableLimit
        elif changeType == 'Increment':
            variableToAdjust += zoomFactor
            if (variableToAdjust > variableLimit): variableToAdjust = variableLimit
        return round(variableToAdjust, 3)
    if zoomType == 'ZoomIn':
        if ((variableMaximum-zoomFactor) - (variableMinimum+zoomFactor)) < variableRangeLimit: zoomFactor = ((variableMaximum - variableMinimum)-variableRangeLimit)/2
        variableMinimum += zoomFactor
        variableMaximum -= zoomFactor
        return round(variableMinimum, 3), round(variableMaximum, 3)

def findIndexOfNearestValue(array, value):
    array = np.asarray(array)
    index = (np.abs(array - value)).argmin()
    return index         
                    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


