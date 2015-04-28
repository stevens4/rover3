# BOILERPLATE ##
import sys
from PySide import QtGui, QtCore
if QtCore.QCoreApplication.instance() is None:    
    app = QtGui.QApplication(sys.argv)
    import qt4reactor
    qt4reactor.install()
## BOILERPLATE ##

# LED indicator
from qtutils.qled import LEDWidget



INTERLOCK_DISABLED_ICON = QtGui.QIcon.fromTheme("emblem-important") 
INTERLOCK_ENABLED_ICON = QtGui.QIcon.fromTheme("emblem-readonly")
INTERLOCK_CONFIG_ICON = QtGui.QIcon.fromTheme("help-contents")
INTERLOCK_ADD_ICON = QtGui.QIcon.fromTheme("address-book-new")
INTERLOCK_DEL_ICON = QtGui.QIcon.fromTheme("edit-delete")



'''
a customized widget for controlling a relay and its associated interlocks
'''

class doControlRow(QtGui.QWidget):
    def __init__(self,deviceName,doObject):
        # static class variables
        self.deviceName = deviceName
        self.doObject = doObject
        
        # dynamic class variables
        self.enabled = self.doObject.getState()
        self.interlocked = self.doObject.getInterlockState()
        
        # set up the layout
        QtGui.QWidget.__init__(self)
        self.setLayout(QtGui.QGridLayout())
        
        # add a status LED
        LED = LEDWidget()
        self.layout().addWidget(LED,1,1)
        
        # add a toggle button
        def onToggle():
            if self.enabled:
                print 'turning off '+self.deviceName
                LED.toggle()
                toggleButton.setText("turn on")
                interlockEnableButton.setEnabled(False)
                interlockDialogButton.setEnabled(False)
                self.doObject.setState(False)
            if not self.enabled:
                print 'turning on '+self.deviceName
                LED.toggle()
                toggleButton.setText("turn off")
                interlockEnableButton.setEnabled(True)
                interlockDialogButton.setEnabled(True)
                self.doObject.setState(True)
            self.enabled = not self.enabled
        toggleButton = QtGui.QPushButton("turn on")
        toggleButton.clicked.connect(onToggle)
        self.layout().addWidget(toggleButton,1,2)
        
        # add a label
        label = QtGui.QLabel(self.doObject.labelText)
        label.setFont(QtGui.QFont("Helvetica [Cronyx]", 18))
        label.setEnabled(self.enabled)
        self.layout().addWidget(label,1,3)
        self.layout().setColumnStretch(3,5) # make the label soak up extra space
        
        # add a interlock enable
        def interlockToggle():
            if self.interlocked:
                print 'disabling interlocks for '+self.deviceName
                interlockEnableButton.setIcon( INTERLOCK_DISABLED_ICON )
                self.interlocked = False
                for interlock in self.doObject.getInterlocks().values():
                    interlock.setState(False)
                return
            if not self.interlocked:                        
                print 'enabling interlocks for '+self.deviceName
                interlockEnableButton.setIcon( INTERLOCK_ENABLED_ICON )
                self.interlocked = True
                for interlock in self.doObject.getInterlocks().values():
                    interlock.setState(True)
                return
        interlockEnableButton = QtGui.QPushButton()
        interlockEnableButton.setIcon( INTERLOCK_DISABLED_ICON )
        interlockEnableButton.setEnabled(False)
        interlockEnableButton.clicked.connect(interlockToggle)
        self.layout().addWidget(interlockEnableButton,1,4)
        
        # add a interlock config dialog
        def interlockDialogClicked():
            configDialog = interlockConfig(self.deviceName,self.doObject)
        interlockDialogButton = QtGui.QPushButton()
        interlockDialogButton.setIcon( INTERLOCK_CONFIG_ICON )
        interlockDialogButton.setEnabled(False)
        interlockDialogButton.clicked.connect(interlockDialogClicked)
        self.layout().addWidget(interlockDialogButton,1,5)
        
        # run click events on buttons depending on initial state
        if self.enabled: 
            self.enabled = False
            onToggle()
        if self.interlocked:
            self.interlocked = False
            interlockToggle()
        


'''
a customized version of pyside's dialog box. this is used for configuring
the interlocks for a given relay control.

'''
class interlockConfig(QtGui.QDialog):
    def __init__(self,doName,digitalOutputObj):
        # set class variables
        self.doName = doName
        self.doObj = digitalOutputObj
        
        # read in this DO object's existing interlocks and their config dict, create swap
        existingInterlocks = self.doObj.getInterlocks()
        self.interlocksConf = {}
        for interlockKey,interlock in existingInterlocks.items():
            self.interlocksConf[interlockKey] = interlock.getConfDict()
        self.interlockSwapConf = {}
        for interlockKey, interlockConfDict in self.interlocksConf.items():
            self.interlockSwapConf[interlockKey] = interlockConfDict
        print self.interlockSwapConf
        
        # set up the GUI options
        QtGui.QDialog.__init__(self)
        self.setLayout(QtGui.QGridLayout())
        self.setWindowTitle('interlocks for '+self.doName)
    
        # make confirm and cancel buttons
        commitCancelRow = 0
        # if save is clicked, update existing interlocks and add new ones
        def okayClicked():
            for interlockKey,interlock in self.doObj.getInterlocks().items():
                print 'deleting interlock '+str(interlockKey)
                self.doObj.deleteInterlock(interlockKey)
            for interlockKey,interlockConfDict in self.interlockSwapConf.items():
                print 'adding new interlock '+str(interlockKey)
                self.doObj.createInterlock(interlockConfDict)
            self.doObj.configUpdate()
            self.accept()
        okayButton = QtGui.QPushButton("save")
        okayButton.clicked.connect(okayClicked)
        self.layout().addWidget(okayButton,commitCancelRow,1,1,2)
        
        # if cancel is clicked, throw out all changes
        def cancelClicked():
            for interlockKey in self.interlockSwapConf.keys():
                del self.interlockSwapConf[interlockKey]
            self.reject()
        cancelButton = QtGui.QPushButton("cancel")
        cancelButton.clicked.connect(cancelClicked)
        self.layout().addWidget(cancelButton,commitCancelRow,3,1,2)
                
        # add a line at the top to configure and add a new interlock    
        addInterlockRow = self.makeNewInterlockRow()
        self.layout().addLayout(addInterlockRow,1,1,1,4)
            
        # add rows for each existing interlock
        for interlockKey, interlockConfDict in self.interlockSwapConf.items(): 
            thisInterlockRow = self.makeExistingInterlockRow(interlockKey,interlockConfDict)
            rowNum = interlockKey + 2
            self.layout().addLayout(thisInterlockRow,rowNum,1,1,4)
    
        # pop the dialog to the screen
        self.exec_()

            
    def makeNewInterlockRow(self):
        thisLayout = QtGui.QGridLayout()
        
        def addClicked():
            # get the current parameters from the add widget
            aiChan = aiChanDropDown.currentText()
            logicalFunc = logFuncDropDown.currentText()
            limitVal = limValSpinBox.value()
            
            # add new interlock conf dict to the swap dict
            newInterlockKey = len(self.interlockSwapConf.keys())
            newInterlockConfDict = {}
            newInterlockConfDict['senseChan'] = aiChan
            newInterlockConfDict['logFun'] = logicalFunc
            newInterlockConfDict['limVal'] = limitVal
            self.interlockSwapConf[newInterlockKey] = newInterlockConfDict
            
            # create a new interlock row for the new interlock
            rowNum = newInterlockKey + 2
            newInterlockRow = self.makeExistingInterlockRow(newInterlockKey,newInterlockConfDict)
            self.layout().addLayout(newInterlockRow,rowNum,1,1,4)
            
        addButton = self._makeAddButton()
        addButton.clicked.connect(addClicked)
        
        aiChanDropDown = self._makeAIDD()
        logFuncDropDown = self._makeLFDD()
        limValSpinBox = self._makeLVSB()
        
        thisLayout.addWidget(addButton,1,1)
        thisLayout.addWidget(aiChanDropDown,1,2)
        thisLayout.addWidget(logFuncDropDown,1,3)
        thisLayout.addWidget(limValSpinBox,1,4)
    
        return thisLayout
        
        
    def makeExistingInterlockRow(self,interlockKey,interlockConfDict):
        thisInterlockKey = interlockKey
        thisInterlockConfDict = interlockConfDict
        thisLayout = QtGui.QGridLayout()
        
        def deleteClicked():
            del self.interlockSwapConf[thisInterlockKey]
            thisLayout.setHidden(True)    
        delButton = self._makeDelButton()
        delButton.clicked.connect(deleteClicked)
        
        aiChanDropDown = self._makeAIDD()
        setThis = aiChanDropDown.findText(thisInterlockConfDict['senseChan'])
        aiChanDropDown.setCurrentIndex(setThis)
        def aiChanUpdate():
            thisInterlockConfDict['senseChan'] = aiChanDropDown.currentText()
        aiChanDropDown.currentIndexChanged.connect(aiChanUpdate)
        
        logFuncDropDown = self._makeLFDD()
        logFunc = thisInterlockConfDict['logFun']
        setThis = logFuncDropDown.findText(logFunc)
        logFuncDropDown.setCurrentIndex(setThis)
        def logFuncUpdate():
            selectedFunction = logFuncDropDown.currentText()
            thisInterlockConfDict['logFun'] = selectedFunction
        logFuncDropDown.currentIndexChanged.connect(logFuncUpdate)
        
        limValSpinBox = self._makeLVSB()
        limValSpinBox.setValue(thisInterlockConfDict['limVal'])
        def limValUpdate():
            thisInterlockConfDict['limVal'] = limValSpinBox.value()
        limValSpinBox.valueChanged.connect(limValUpdate)
        
        thisLayout.addWidget(delButton,1,1)
        thisLayout.addWidget(aiChanDropDown,1,2)
        thisLayout.addWidget(logFuncDropDown,1,3)
        thisLayout.addWidget(limValSpinBox,1,4)
    
        return thisLayout
            
    def _makeAddButton(self):
        # add button
        addButton = QtGui.QPushButton()
        addButton.setIcon( INTERLOCK_ADD_ICON )
        return addButton
        
    def _makeDelButton(self):
        deleteButton = QtGui.QPushButton()
        deleteButton.setIcon( INTERLOCK_DEL_ICON )
        return deleteButton
    
    def _makeAIDD(self):
        # AI channel drop down
        from config import analogInputsConfDict
        aiDropDown = QtGui.QComboBox()
        for aiName in analogInputsConfDict.keys():
            aiDropDown.addItem(aiName)
        return aiDropDown
        
    def _makeLFDD(self):
        # logical function drop down
        logicalFunctionDropDown = QtGui.QComboBox()
        from lowLevelLibrary import LOGICAL_FUNCTIONS
        for funct in LOGICAL_FUNCTIONS.keys():
            logicalFunctionDropDown.addItem(funct)
        return logicalFunctionDropDown
        
    def _makeLVSB(self):
        # limit value spinbox
        limitSpinBox = QtGui.QDoubleSpinBox()
        return limitSpinBox
