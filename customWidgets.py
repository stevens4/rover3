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


# set icons for various interlock buttons. 
from sys import platform
if platform == 'linux2': QtGui.QIcon.setThemeName('gnome')
INTERLOCK_DISABLED_ICON = QtGui.QIcon.fromTheme("emblem-important") 
INTERLOCK_ENABLED_ICON = QtGui.QIcon.fromTheme("emblem-favorite")
INTERLOCK_CONFIG_ICON = QtGui.QIcon.fromTheme("document-open")
INTERLOCK_ADD_ICON = QtGui.QIcon.fromTheme("appointment-new")
INTERLOCK_DEL_ICON = QtGui.QIcon.fromTheme("edit-delete")




#by stevens4, given a dictionary, populates a combo out of the keys and emits
#the associated value via the choiceMade signal.
class DictComboBox(QtGui.QComboBox):
    currentKeyChanged = QtCore.Signal(object)
    def __init__(self,itemsDict=None):
        QtGui.QComboBox.__init__(self)
        self.keysList = []
        self.valsList = []
        if itemsDict != None:
            self.updateCombo(itemsDict)
        def onCurrentIndexChanged(index):
            self.currentKeyChanged.emit(self.valsList[index])
        
        self.currentIndexChanged.connect(onCurrentIndexChanged)
    
    def updateCombo(self,itemsDict):
        self.keysList = []
        self.valsList = []
        self.clear()
        
        for key,val in itemsDict.items():
             self.keysList.append(key)
             self.valsList.append(val)
             self.addItem(key)

    def getCurrentKey(self):
        return self.keysList[self.currentIndex()]
        
    def getCurrentVal(self):
        return self.valsList[self.currentIndex()]
        


'''
a customized widget for controlling a relay and its associated interlocks
'''

class doControlRow(QtGui.QWidget):
    def __init__(self,deviceName,doObject,aiObjDict):
        # static class variables
        self.deviceName = deviceName
        self.doObject = doObject
        self.aiObjDict = aiObjDict
        
        # dynamic class variables
        self.enabled = self.doObject.currentState
        self.interlocked = self.doObject.interlockState
        
        # set up the layout
        QtGui.QWidget.__init__(self)
        self.setLayout(QtGui.QGridLayout())
        
        # add a status LED
        self.LED = LEDWidget(self.enabled)
        self.layout().addWidget(self.LED,1,1)
        
        # add a toggle button
        self.toggleButton = QtGui.QPushButton("turn on")
        if self.enabled: self.toggleButton.setText("turn off")
        self.toggleButton.clicked.connect(self.onToggle)
        self.layout().addWidget(self.toggleButton,1,2)
        
        # add a label
        self.label = QtGui.QLabel(self.doObject.labelText)
        self.label.setFont(QtGui.QFont("Helvetica [Cronyx]", 24))
        self.label.setEnabled(self.enabled)
        self.layout().addWidget(self.label,1,3)
        self.layout().setColumnStretch(3,5) # make the label soak up extra space
        
        # add interlock toggle button
        self.interlockEnableButton = QtGui.QPushButton()
        self.interlockEnableButton.setIcon( INTERLOCK_DISABLED_ICON  )
        if self.interlocked: self.interlockEnableButton.setIcon( INTERLOCK_ENABLED_ICON  )
        self.interlockEnableButton.clicked.connect(self.interlockToggle)
        self.layout().addWidget(self.interlockEnableButton,1,4)
        
        # add a interlock config dialog call button
        def interlockDialogClicked():
            configDialog = interlockConfig(self.deviceName,self.doObject,self.aiObjDict)
        self.interlockDialogButton = QtGui.QPushButton()
        self.interlockDialogButton.setIcon( INTERLOCK_CONFIG_ICON )
        self.interlockDialogButton.clicked.connect(interlockDialogClicked)
        self.layout().addWidget(self.interlockDialogButton,1,5)
        
        # run click events on buttons depending on initial state
        '''
        if self.enabled:
            self.LED.toggle(True)
            self.toggleButton.setText("turn off")
            self.label.setEnabled(True)
        if self.interlocked:
            self.interlockEnableButton.setIcon( INTERLOCK_ENABLED_ICON )
            for interlock in self.doObject.getInterlocks().values():
                interlock.setState(True)
        '''
        
    def onToggle(self):
        if self.enabled:
            self.LED.toggle()
            self.toggleButton.setText("turn on")
            self.label.setEnabled(False)
            #self.interlockEnableButton.setEnabled(False)
            #self.interlockDialogButton.setEnabled(False)
            self.doObject.setState(False)
            if self.interlocked: self.interlockToggle()
        if not self.enabled:
            self.LED.toggle()
            self.toggleButton.setText("turn off")
            self.label.setEnabled(True)
            #self.interlockEnableButton.setEnabled(True)
            #self.interlockDialogButton.setEnabled(True)
            self.doObject.setState(True)
        self.enabled = not self.enabled
        
    # add a interlock enable
    def interlockToggle(self):
        if self.interlocked:
            print self.deviceName+' interlocks have been turned OFF'
            self.interlockEnableButton.setIcon( INTERLOCK_DISABLED_ICON )
            self.interlocked = False
            self.doObject.interlockState = False
            return
        if not self.interlocked:                        
            print self.deviceName+' interlocks have been turned ON'
            self.interlockEnableButton.setIcon( INTERLOCK_ENABLED_ICON )
            self.interlocked = True
            self.doObject.interlockState = True
            return
        
    def interlockTrip(self):
        self.onToggle()


'''
a customized version of pyside's dialog box. this is used for configuring
the interlocks for a given relay control.

'''
class interlockConfig(QtGui.QDialog):
    def __init__(self,doName,digitalOutputObj,aiObjDict):
        # set class variables
        self.doName = doName
        self.doObj = digitalOutputObj
        self.aiObjDict = aiObjDict
        
        # read in this DO object's existing interlocks and their config dict, create swap
        existingInterlocks = self.doObj.getInterlocks()
        self.interlocksConf = {}
        for interlockKey,interlock in existingInterlocks.items():
            self.interlocksConf[interlockKey] = interlock.getConfDict()
        self.interlockSwapConf = {}
        for interlockKey, interlockConfDict in self.interlocksConf.items():
            self.interlockSwapConf[interlockKey] = interlockConfDict
        
        # set up the GUI options
        QtGui.QDialog.__init__(self)
        self.setLayout(QtGui.QGridLayout())
        self.setWindowTitle('interlocks for '+self.doName)
    
        # make confirm and cancel buttons
        commitCancelRow = 0
        # if save is clicked, update existing interlocks and add new ones
        def okayClicked():
            for interlockKey,interlock in self.doObj.getInterlocks().items():
                print self.doName+' deleting interlock on '+interlock.aiChannelName+' '+interlock.logicalFunction+' '+str(interlock.limitValue)
                self.doObj.deleteInterlock(interlockKey)
            for interlockKey,interlockConfDict in self.interlockSwapConf.items():
                print self.doName+' creating interlock on '+interlockConfDict['senseChan']+' '+interlockConfDict['logFun']+' '+str(interlockConfDict['limVal'])
                self.doObj.createInterlock(interlockConfDict,self.aiObjDict[interlockConfDict['senseChan']])
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
            aiChanName = aiChanDropDown.getCurrentKey()
            aiChanObj = aiChanDropDown.getCurrentVal()
            logicalFunc = logFuncDropDown.currentText()
            limitVal = limValSpinBox.value()
            
            # add new interlock conf dict to the swap dict
            newInterlockKey = len(self.interlockSwapConf.keys())
            newInterlockConfDict = {}
            newInterlockConfDict['senseChan'] = aiChanName
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
            delButton.setEnabled(False)
            aiChanDropDown.setEnabled(False)
            logFuncDropDown.setEnabled(False)
            limValSpinBox.setEnabled(False)
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
        aiDropDown = DictComboBox()
        aiDropDown.updateCombo(self.aiObjDict)
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
