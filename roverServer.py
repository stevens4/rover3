'''
by stevens4

this is the main program that runs on Rover3.

it has functionality to log its state, reload its former state upon
start, adjust the state of digital outputs (channels specified in rover.
config) by user control or by interlock automation.

it will also publish information (but NOT control) to the client.

'''

## BOILERPLATE ##
import sys
from PySide import QtGui, QtCore
if QtCore.QCoreApplication.instance() is None:    
    app = QtGui.QApplication(sys.argv)
    import qt4reactor
    qt4reactor.install()
## BOILERPLATE ##


# to get all funky with function specifiers
from functools import partial

# config for channels and logPath
from config import analogInputsConfDict, digitalOutputsConfDict, roverLogPath

# analog input and digital output channel objects
from lowLevelLibrary import aiChannel, doChannel

# customized layout and dialog for DO controls
from customWidgets import doControlRow, interlockConfig

# LogFile object for transcript and statusFile
#from filecreationmethods import LogFile

# import basic os filesystem methods
import os

# handy config methods for interlocks saving/editing
import ConfigParser

from time import sleep

# to preserve order in dictionaries
from collections import OrderedDict

import sys
from datetime import datetime

############################### logging ###########################

DEBUG = False

# overwrite the print statement to prepend a timestamp & write these to the transcript file
transcriptFilename = os.path.join(roverLogPath, 'roverTranscript.txt')
transcriptFile = open(transcriptFilename,'a',0)
oldPrint = sys.stdout
if DEBUG: oldPrint = sys.stdout
else: oldPrint = transcriptFile
class newPrint():
    def write(self,x):
        if x == '\n':
            oldPrint.write(x)
        else:
            oldPrint.write('['+str(datetime.now())+']\t'+x)
sys.stdout = newPrint()


################################## set up the GUI ######################
class RoverWidget(QtGui.QWidget):
    def __init__(self):
        self.closeRequested = False
        self.loopDone = True
        
        # initialize dictionary of analog inputs and fill with our channels
        aiDummy = {}
        for aiName, aiConf in analogInputsConfDict.items():
            aiDummy[aiName] = aiChannel(aiConf)
        self.analogInputs = OrderedDict(sorted(aiDummy.items(), key=lambda k: k[0]))
        
        # create the handle to the startup state file (this is the toggle state of each DO)
        self.startStateFilename = os.path.join(roverLogPath, 'startState.txt')
        self.startStateConfigParser = ConfigParser.RawConfigParser()
        self.startStateConfigParser.read(self.startStateFilename)
        
        # initialize dictionary of digital outputs and fill with our channels, set to state file
        print 'creating relay toggles...'
        doDummy = {}
        for doName, doConf in digitalOutputsConfDict.items():
            doConf['name'] = doName
            if doName in self.startStateConfigParser.sections():
                initState = self.startStateConfigParser.get(doName,'initState')
                initInterlockState = self.startStateConfigParser.get(doName,'initInterlockState')
            else:
                print 'could not find '+doName+' in state file. resetting to off.'
                initState = False
                initInterlockState = False
                
            doConf['initState'] = initState
            doConf['initInterlockState'] = initInterlockState
            doDummy[doName] = doChannel(doConf,self.analogInputs) #give each DO object the aiChanDict so it can make its interlocks at start
            
        self.digitalOutputs = OrderedDict(sorted(doDummy.items(), key=lambda k: k[0]))
        print 'done creating relays.'
        
        # set general layout things
        QtGui.QWidget.__init__(self)
        self.setLayout(QtGui.QGridLayout()) # 10 columns wide
        self.layout().setHorizontalSpacing(15)
        self.layout().setVerticalSpacing(10)
        self.layout().setColumnMinimumWidth(5,20)
        self.layout().setRowMinimumHeight(5,20)
            
            
        # create a space spanning the full width at the top for the water
        waterTempLayout = QtGui.QHBoxLayout()
        waterTempConf = analogInputsConfDict['water temperature']
        
        waterLabel = QtGui.QLabel(waterTempConf['labelText'])
        waterLabel.setFont(QtGui.QFont("Helvetica [Cronyx]", 40))
        waterLabel.setAlignment(QtCore.Qt.AlignHCenter)
        self.layout().addWidget(waterLabel,0,3,1,3)
        
        waterLCD = QtGui.QLCDNumber(3)
        waterLCD.setSegmentStyle(QtGui.QLCDNumber.Flat)
        waterLCD.setFrameStyle(QtGui.QFrame.NoFrame)
        waterLCD.setNumDigits(6)
        waterLCD.display(20.05)
        self.layout().addWidget(waterLCD,0,6,1,1)
        
        self.analogInputs['water temperature'].LCD = waterLCD
        
        #self.layout().addLayout(waterTempLayout,waterTempConf['guiRow'],waterTempConf['guiColumn'],1,4)
        
        # create column headers for the two chambers
        poohLabel = QtGui.QLabel("pooh")
        poohLabel.setFont(QtGui.QFont("Helvetica [Cronyx]", 40))
        poohLabel.setAlignment(QtCore.Qt.AlignHCenter)
        self.layout().addWidget(poohLabel,1,0,1,5)
        
        tiggerLabel = QtGui.QLabel("tigger")
        tiggerLabel.setFont(QtGui.QFont("Helvetica [Cronyx]", 40))
        tiggerLabel.setAlignment(QtCore.Qt.AlignHCenter)
        self.layout().addWidget(tiggerLabel,1,5,1,5)
        
        # create a layout for each AI and add to specified layout
        for aiName, aiConf in analogInputsConfDict.items():
            if aiName == 'water temperature': continue
            thisRowNumber = aiConf['guiRow']
            thisColumnStartNumber = aiConf['guiColumn']
            thisLayout = QtGui.QHBoxLayout()
            
            thisLabel = QtGui.QLabel(aiConf['labelText'])
            thisLabel.setFont(QtGui.QFont("Helvetica [Cronyx]", 40))
            thisLabel.setAlignment(QtCore.Qt.AlignRight)
            self.layout().addWidget(thisLabel,thisRowNumber,thisColumnStartNumber)
            
            thisLCD = QtGui.QLCDNumber(6)
            thisLCD.setSegmentStyle(QtGui.QLCDNumber.Flat)
            thisLCD.setFrameStyle(QtGui.QFrame.NoFrame)
            thisLCD.display(030)
            self.layout().addWidget(thisLCD,thisRowNumber,thisColumnStartNumber+1,1,3)
            
            self.analogInputs[aiName].LCD = thisLCD
            
            #self.layout().addLayout(thisLayout,thisRowNumber,thisColumnStartNumber,1,3)
                
        # create a layout for each DO and add to specified layout
        self.doControlRows = []
        for doName, doObj in self.digitalOutputs.items():
            thisDOControlRow = doControlRow(doName,doObj,self.analogInputs)
            rowToPlace = doObj.confDict['guiRow']
            colToPlace = doObj.confDict['guiColumn']
            self.layout().addWidget(thisDOControlRow,rowToPlace,colToPlace,1,5)
            self.doControlRows.append(thisDOControlRow)
            
        # enter the update loop
        orderToReadDict = {}
        for aiChanObj in self.analogInputs.values():
            orderToReadDict[aiChanObj.readOrder] = aiChanObj
        import operator
        self.orderToRead = sorted(orderToReadDict.items(), key=operator.itemgetter(0))
        import threading
        thread = threading.Thread(target=self._loop)
        thread.setDaemon(True)
        thread.start()
        
    def _loop(self):
        for order,aiChanObj in self.orderToRead:
            # check if GUI is trying to close
            if self.closeRequested:
                self.threadDone = True
                return
            else:
                self.threadDone = False
            # read new values on this sensor
            try:
                newReading = aiChanObj.getNReadings(200)
                aiChanObj.LCD.display(newReading)
            except TypeError:
                print 'lost connection to ADC. retrying in .5s...'
                sleep(.5)
                self._loop()
            
            # check all relays' interlocks based on new sensor value
            for thisDOControlRow in self.doControlRows:
                relayEnabled = thisDOControlRow.doObject.currentState
                if not relayEnabled: continue #skip if this DO is off
                
                interlockEnabled = thisDOControlRow.doObject.interlockState
                if not interlockEnabled: continue #skip if interlocks are overriden
                
                # iterate through this DO's interlocks and check values
                interlockTripped = thisDOControlRow.doObject.testInterlocks()
                if interlockTripped:
                    thisDOControlRow.toggleButton.click()
        self._loop()
    
    def closeEvent(self, event):
        # tell the loop thread you're looking to close, so it can stop
        self.closeRequested = True
        
        # update state file so that current DO on/off state persists on next run
        print 'asked to shutdown. writing state file...'
        
        if DEBUG: print "relay name\t\t\t\tpower\tinterlocked"
        
        for doName, doObj in self.digitalOutputs.items():
            state = doObj.getState() in [1]
            interlocksDict = doObj.getInterlocks()
            interlockState = doObj.interlockState
            if doName not in self.startStateConfigParser.sections():
                self.startStateConfigParser.add_section(doName)
            self.startStateConfigParser.set(doName, 'initState', state)
            self.startStateConfigParser.set(doName, 'initInterlockState', interlockState)
            
            numTabs = 5-(len(doName)/8)
            tabs = '\t'*numTabs
            if DEBUG: print doName+tabs+str(state)+'\t'+str(interlockState)
            
            
        with open(self.startStateFilename, 'wb') as configfile:
            self.startStateConfigParser.write(configfile)
            
        import RPi.GPIO as GPIO
        #GPIO.cleanup()
        
        # don't close until loop has said it's no longer running
        while not self.threadDone:
            sleep(.1)
        event.accept()

def main(container):
    widget = RoverWidget()
    widget.show()
    container.append(widget)
    widget.setWindowTitle('rover server')

if __name__ == '__main__':
    container = []
    main(container)
    app.exec_()
    

