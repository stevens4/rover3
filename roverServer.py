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

# LED indicator
from qtutils.qled import LEDWidget

# config for channels and logPath
from config import analogInputsConfDict, digitalOutputsConfDict, roverLogPath

# analog input and digital output channel objects
from lowLevelLibrary import aiChannel, doChannel

# LogFile object for transcript and statusFile
#from filecreationmethods import LogFile

# import basic os filesystem methods
import os


# create the transcript file handle
transcriptFilename = os.path.join(roverLogPath, 'roverTranscript.tsv')
#transcript = LogFile(transcriptFilename)

# create the handle to the status file
statusFilename = os.path.join(roverLogPath, 'roverStatus.tsv')
#statusFile = LogFile(statusFilename)
#lastState = statusFile.readLastLine()



# set up the GUI
class RoverWidget(QtGui.QWidget):
    def __init__(self):
		# initialize dictionary of analog inputs and fill with our channels
		self.analogInputs = {}
		for aiName, aiConf in analogInputsConfDict.items():
			print 'creating '+aiName+' ...'
			aiConf['name'] = aiName
			self.analogInputs[aiName] = aiChannel(aiConf)

		# initialize dictionary of digital outputs and fill with our channels
		self.digitalOutputs = {}
		for doName, doConf in digitalOutputsConfDict.items():
			print 'creating '+doName+' ...'
			doConf['name'] = doName
			self.digitalOutputs[doName] = doChannel(doConf)
			#lastState = statusFile.getLast(doName)
			#digitalOutputs[aiName].setState(lastState)
			
		# init dictionary of layouts for DO controls
		self.doControls = {}
			
		# begin GUI stuff
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
		waterLabel.setFont(QtGui.QFont("Helvetica [Cronyx]", 18))
		waterLabel.setAlignment(QtCore.Qt.AlignHCenter)
		waterTempLayout.addWidget(waterLabel)
		
		waterLCD = QtGui.QLCDNumber(3)
		waterLCD.setSegmentStyle(QtGui.QLCDNumber.Flat)
		waterLCD.setFrameStyle(QtGui.QFrame.NoFrame)
		waterLCD.display(030)
		waterTempLayout.addWidget(waterLCD)
		
		self.layout().addLayout(waterTempLayout,waterTempConf['guiRow'],waterTempConf['guiColumn'],1,4)
		
		
		# create column headers for the two chambers
		poohLabel = QtGui.QLabel("pooh")
		poohLabel.setFont(QtGui.QFont("Helvetica [Cronyx]", 36))
		poohLabel.setAlignment(QtCore.Qt.AlignHCenter)
		self.layout().addWidget(poohLabel,1,0,1,5)
		
		tiggerLabel = QtGui.QLabel("tigger")
		tiggerLabel.setFont(QtGui.QFont("Helvetica [Cronyx]", 36))
		tiggerLabel.setAlignment(QtCore.Qt.AlignHCenter)
		self.layout().addWidget(tiggerLabel,1,5,1,5)
		
		# create a layout for each AI and add to specified layout
		for aiName, aiConf in analogInputsConfDict.items():
			if aiName == 'water temperature': continue
			thisRowNumber = aiConf['guiRow']
			thisColumnStartNumber = aiConf['guiColumn']
			thisLayout = QtGui.QHBoxLayout()
			
			thisLabel = QtGui.QLabel(aiConf['labelText'])
			thisLabel.setFont(QtGui.QFont("Helvetica [Cronyx]", 18))
			thisLabel.setAlignment(QtCore.Qt.AlignRight)
			thisLayout.addWidget(thisLabel)
			
			thisLCD = QtGui.QLCDNumber(3)
			thisLCD.setSegmentStyle(QtGui.QLCDNumber.Flat)
			thisLCD.setFrameStyle(QtGui.QFrame.NoFrame)
			thisLCD.display(030)
			thisLayout.addWidget(thisLCD)
			
			self.layout().addLayout(thisLayout,thisRowNumber,thisColumnStartNumber,1,2)
			
		# define the control row object. we will instantiate one of these for each DO object.
		class doControl():
			def __init__(self,deviceName=None,LED=None,toggleButton=None,interlockEnableButton=None,interlockDialogButton=None):
				self.deviceName = deviceName
				self.LED = LED
				self.toggleButton = toggleButton
				self.interlockEnableButton = interlockEnableButton
				self.interlockDialogButton = interlockDialogButton
				self.enabled = False
				self.interlocked = False
				self.doObject = None
				
		# create a layout for each DO and add to specified layout
		for doName, doConf in digitalOutputsConfDict.items():
			
			# LED
			thisLED = LEDWidget()
			self.layout().addWidget(thisLED,doConf['guiRow'],doConf['guiColumn'])
			
			# toggle button
			def onToggle(doName):
				doToToggle = self.doControls[doName]
				if doToToggle.enabled:
					print 'turning off '+doToToggle.deviceName
					doToToggle.LED.toggle()
					doToToggle.toggleButton.setText("turn on")
					doToToggle.doObject.setState(False)
					doToToggle.interlockEnableButton.setEnabled(False)
					doToToggle.interlockDialogButton.setEnabled(False)
					
				if not doToToggle.enabled:
					print 'turning on '+doToToggle.deviceName
					doToToggle.LED.toggle()
					doToToggle.toggleButton.setText("turn off")
					doToToggle.doObject.setState(True)
					doToToggle.interlockEnableButton.setEnabled(True)
					doToToggle.interlockDialogButton.setEnabled(True)
					
				doToToggle.enabled = not doToToggle.enabled
				doToToggle.toggleButton.setChecked(False)
			
			thisToggle = QtGui.QPushButton("turn on")
			thisToggle.clicked.connect(partial(onToggle,doName))
			#thisToggle.setCheckable(True)
			self.layout().addWidget(thisToggle,doConf['guiRow'],doConf['guiColumn']+1)
			
			# label
			thisLabel = QtGui.QLabel(doConf['labelText'])
			thisLabel.setFont(QtGui.QFont("Helvetica [Cronyx]", 18))
			self.layout().addWidget(thisLabel,doConf['guiRow'],doConf['guiColumn']+2)
			
			# interlock enable
			def interlockToggle(doName):
				doToToggle = self.doControls[doName]
				if doToToggle.interlocked:
					print 'disabling interlocks for '+doToToggle.deviceName
					doToToggle.interlockEnableButton.setIcon( QtGui.QIcon.fromTheme("emblem-important") )
					doToToggle.interlocked = False
					return
				
				if not doToToggle.interlocked:						
					print 'enabling interlocks for '+doToToggle.deviceName
					doToToggle.interlockEnableButton.setIcon( QtGui.QIcon.fromTheme("emblem-readonly") )
					doToToggle.interlocked = True
					return
				
			thisInterlockEnable = QtGui.QPushButton()
			thisInterlockEnable.setEnabled(False)
			#thisInterlockEnable.setCheckable(True)
			thisInterlockEnable.setIcon( QtGui.QIcon.fromTheme("emblem-important") )
			thisInterlockEnable.clicked.connect(partial(interlockToggle,doName))
			self.layout().addWidget(thisInterlockEnable,doConf['guiRow'],doConf['guiColumn']+3)
			
			# interlock help
			def interlockConfig(doName):
				# set up a dialog window to pop
				configDialog = QtGui.QDialog()
				configDialog.setLayout(QtGui.QGridLayout())
				configDialog.setWindowTitle('interlocks for '+doName)
				
				
				# load the existing interlocks from the do object. create a swap version
				self.oldInterlocks = {}
				self.thisDO = self.digitalOutputs[doName]
				self.oldInterlocks = self.thisDO.getInterlocks()
				configDialog.newInterlocksSwap = {}
				for key, interlock in self.oldInterlocks.items():
					configDialog.newInterlocksSwap[key] = interlock

				# create an interlock config row object
				class interlockRow():
					def __init__(self,doObj,interlockKey=None,interlockObj=None):
						self.interlockConfig = configDialog
						self.doObject = doObj
						self.interlockKey = interlockKey
						self.interlockObj = interlockObj
						self.guiItems = []
						
						if self.interlockKey is not None:
							# delete button
							def deleteClicked():
								del self.interlockConfig.newInterlocksSwap[self.interlockKey]
								for guiItem in self.guiItems:
									guiItem.setHidden(True)
							deleteButton = QtGui.QPushButton()
							deleteButton.setIcon( QtGui.QIcon.fromTheme("edit-delete") )
							deleteButton.clicked.connect(deleteClicked)
							self.guiItems.append(deleteButton)
							
						else:
							# add button
							def addClicked():
								# get the current parameters from the add widget
								aiChan = aiDropDown.currentText()
								logicalFunc = logicalFunctionDropDown.currentText()
								limitVal = limitSpinBox.value()
								
								# add new interlock to the swap dict
								newInterlockKey = len(self.interlockConfig.newInterlocksSwap.keys())
								from lowLevelLibrary import interlock
								newInterlock = interlock(aiChan,limitVal,logicalFunc)
								self.interlockConfig.newInterlocksSwap[newInterlockKey] = newInterlock
								
								# create a new interlock row for the new interlock
								rowNum = newInterlockKey + 2
								newInterlockRow = interlockRow(self.doObject,interlockKey=newInterlockKey,interlockObj=newInterlock)
								for colNum, guiItem in enumerate(newInterlockRow.guiItems):
									self.interlockConfig.layout().addWidget(guiItem,rowNum,colNum)
								
							addButton = QtGui.QPushButton()
							addButton.setIcon( QtGui.QIcon.fromTheme("address-book-new") )
							addButton.clicked.connect(addClicked)
							self.guiItems.append(addButton)
								
						# AI channel drop down
						aiDropDown = QtGui.QComboBox()
						for aiName in analogInputsConfDict.keys():
							aiDropDown.addItem(aiName)
						self.guiItems.append(aiDropDown)
						if self.interlockObj is not None:
							setThis = aiDropDown.findText(self.interlockObj.getSenseChannel())
							aiDropDown.setCurrentIndex(setThis)
							aiDropDown.currentIndexChanged.connect(self.interlockObj.setSenseChannel)
						
						# logical function drop down
						logicalFunctionDropDown = QtGui.QComboBox()
						from lowLevelLibrary import LOGICAL_FUNCTIONS
						for funct in LOGICAL_FUNCTIONS.keys():
							logicalFunctionDropDown.addItem(funct)
						self.guiItems.append(logicalFunctionDropDown)
						if self.interlockObj is not None:
							logFunc = self.interlockObj.getLogicalFunction()
							setThis = logicalFunctionDropDown.findText(logFunc)
							logicalFunctionDropDown.setCurrentIndex(setThis)
							def update():
								selectedFunction = logicalFunctionDropDown.currentText()
								self.interlockObj.setLogicalFunction(selectedFunction)
							logicalFunctionDropDown.currentIndexChanged.connect(update)
						
						# limit value spinbox
						limitSpinBox = QtGui.QDoubleSpinBox()
						self.guiItems.append(limitSpinBox)
						if self.interlockObj is not None:
							limitSpinBox.setValue(self.interlockObj.getLimitValue())
							limitSpinBox.valueChanged.connect(self.interlockObj.setLimitValue)
						
							
				# add a confirm/cancel row at the top to commit or clear changes
				commitCancelRow = 0
				def okayClicked():
					for key,interlock in configDialog.newInterlocksSwap.items():
						if key in self.oldInterlocks.keys():
							oldInterlock = self.oldInterlocks[key]							
							oldInterlock.setSenseChannel(interlock.getSenseChannel())
							oldInterlock.setLogicalFunction(interlock.getLogicalFunction())
							oldInterlock.setLimitValue(interlock.getLimitValue())
						else:
							print 'adding new interlock'
							self.thisDO.addInterlock(interlock)
						configDialog.newInterlocksSwap = {}
					configDialog.accept()
						
				okayButton = QtGui.QPushButton("save")
				okayButton.clicked.connect(okayClicked)
				configDialog.layout().addWidget(okayButton,commitCancelRow,0,1,2)
				
				def cancelClicked():
					configDialog.newInterlocksSwap = {}
					configDialog.reject()
				cancelButton = QtGui.QPushButton("cancel")
				cancelButton.clicked.connect(cancelClicked)
				configDialog.layout().addWidget(cancelButton,commitCancelRow,2,1,2)
						
				# add a line at the top to configure and add a new interlock	
				addInterlockRowNum = 1
				addInterlockRow = interlockRow(thisDOControl)
				for colPos, guiItem in enumerate(addInterlockRow.guiItems):
					configDialog.layout().addWidget(guiItem,addInterlockRowNum,colPos)
					
				# list the existing interlocks
				self.interlockRows = {}
				for interlockKey, interlock in configDialog.newInterlocksSwap.items(): 
					thisInterlockRow = interlockRow(thisDOControl,interlockKey,interlockObj=interlock)
					self.interlockRows[len(self.interlockRows.keys())] = thisInterlockRow
					rowNum = interlockKey + 2
					for colPos, guiItem in enumerate(thisInterlockRow.guiItems):
						configDialog.layout().addWidget(guiItem,rowNum,colPos)
				
				configDialog.exec_()
			
			thisInterlockDialogToggle = QtGui.QPushButton()
			thisInterlockDialogToggle.setIcon( QtGui.QIcon.fromTheme("help-contents") )
			thisInterlockDialogToggle.setEnabled(False)
			thisInterlockDialogToggle.clicked.connect(partial(interlockConfig,doName))
			self.layout().addWidget(thisInterlockDialogToggle,doConf['guiRow'],doConf['guiColumn']+4)
			
			# bundle all these together into the DO control object and add to dict
			thisDOControl = doControl(
				deviceName = doName,
				LED = thisLED,
				toggleButton = thisToggle,
				interlockEnableButton = thisInterlockEnable,
				interlockDialogButton = thisInterlockDialogToggle
			)
			
			thisDOControl.doObject = self.digitalOutputs[doName]
			
			self.doControls[doName] = thisDOControl
		
	
	

def main(container):
    widget = RoverWidget()
    widget.show()
    container.append(widget)
    widget.setWindowTitle('rover server')

if __name__ == '__main__':
	container = []
	main(container)
	app.exec_()
	
import RPi.GPIO as GPIO
GPIO.cleanup()
