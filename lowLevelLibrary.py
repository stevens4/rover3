
from Adafruit_ADS1x15 import ADS1x15 as A2DObject

from functools import partial

# create AI channel objects
class aiChannel:
    def __init__(self,confDict):
        #open connection on physicalChannel
        self.name = confDict['labelText']
        self.i2cAddress = confDict['i2cAddress']
        self.connectionType = confDict['connectionType']
        self.physChan = confDict['physicalChannel']
        self.gain = confDict['gainFactor']
        self.rate = confDict['sampleRate']
        self.LCD = None
        self.mapStyle = confDict['mappingStyle']
        self.mapParams = confDict['mapParams']
        self.units = confDict['mappedUnits']
        self.connection = A2DObject(address=self.i2cAddress)
        self.readOrder = confDict['readOrder']
    
    # gets the latest raw, measured voltage off the ADC
    def getLatestVoltage(self):
        if self.connectionType == 'RSE':
            return self.connection.readADCSingleEnded( 
                channel=self.physChan, 
                pga=self.gain,
                sps=self.rate
            )
        elif self.connectionType == 'diff':
            return self.connection.readADCDifferential(
                chP=self.physChan[0], chN=self.physChan[1],
                pga=self.gain,
                sps=self.rate
            )
        else:
            print 'UNKNOWN CONNECTION TYPE SPECIFIED!!!'
            return 0
       
    # maps the raw voltage to a reading (e.g. volts -> pressure)
    def _map(self,voltage):
        if self.mapStyle == 'poly':
            reading = self.mapParams[0]
            reading += self.mapParams[1]*voltage
            reading += self.mapParams[2]*voltage**2
            reading += self.mapParams[3]*voltage**3
            reading += self.mapParams[4]*voltage**4
        elif self.mapStyle == 'exp':
            reading = self.mapParams[0]*(self.mapParams[1]**voltage)
        else:
            reading = 0
            print 'no mapping style was defined!'
        return reading
        
    # gets the latest reading off the ADC
    def getLastReading(self):
        newVoltage = self.getLatestVoltage()
        newReading = self._map(newVoltage)
        if self.LCD is not None:
            self.LCD.display(newReading)
        return newReading
        
    # gets N readings and returns the average
    def getNReadings(self,nSamp):
        if self.connectionType == 'RSE':
            self.connection.startContinuousConversion(
                channel = self.physChan, 
                pga = self.gain,
                sps = self.rate
                )  
            total = 0.
            for i in range(nSamp):
                total += self.connection.getLastConversionResults()
            self.connection.stopContinuousConversion()
            result = self._map(total/nSamp)
            return result
     
        elif self.connectionType == 'diff':
            self.connection.startContinuousDifferentialConversion(
                chP=self.physChan[0], chN=self.physChan[1],
                pga=self.gain,
                sps=self.rate
            )
            total = 0.
            for i in range(nSamp):
                total += self.connection.getLastConversionResults()
            self.connection.stopContinuousConversion()
            result = self._map(total/nSamp)
            return result
            
        else:
            print 'UNKNOWN CONNECTION TYPE SPECIFIED!!!'
            return 0
       
        
        

from config import roverLogPath
import ConfigParser
import os
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)  # use pin numberings printed on cobbler
GPIO.setwarnings(False) # silence overuse warnings in case you have two DO's on same pin

# create DO channel objects
class doChannel:
    def __init__(self,confDict,aiChanDict,clockFunct=None):
        # read in static class variables
        self.name = confDict['name']
        self.physChanNum = confDict['physicalChannel']
        self.labelText = confDict['labelText']
        self.aiChanDict = aiChanDict
        self.clockFunction = clockFunct
        
        
        self.currentState = False
        GPIO.setup(self.physChanNum,GPIO.OUT)
        
        initState = confDict['initState'] in ['True']
        self.setState(initState)
        
        self.interlockState = False
        initInterlockState = confDict['initInterlockState'] in ['True']
        self.setInterlockState(initInterlockState)
        
        self.interlocks = {}
        self.confDict = confDict
        
        # initialize interlock configparser object, read in
        self.interlockConfigParser = ConfigParser.RawConfigParser()
        self.interlockConfigFilename = os.path.join(roverLogPath, 'interlockConfigs', 'interlockConfig_'+self.name+'.txt')
        self.interlockConfigParser.read(self.interlockConfigFilename)
        
        # parse the interlocks config dicts and create each
        for interlockKey in self.interlockConfigParser.sections():
            thisInterlockConfDict = {}
            thisInterlockConfDict['senseChan'] = self.interlockConfigParser.get(interlockKey, 'senseChan')
            thisInterlockConfDict['logFun'] = self.interlockConfigParser.get(interlockKey, 'logFun')
            thisInterlockConfDict['limVal'] = float(self.interlockConfigParser.get(interlockKey, 'limVal'))
            thisAIChanObj = self.aiChanDict[thisInterlockConfDict['senseChan']]
            thisInterlock = self.createInterlock(thisInterlockConfDict,thisAIChanObj,key=int(interlockKey))
            
  
  
    def setState(self, newState):
        GPIO.output(self.physChanNum, newState)
        
        if self.clockFunction is not None:
            self.clockFunction()
        
        self.currentState = newState
        if newState == True: stateStr = 'ON'
        if newState == False: stateStr = 'OFF'
        print self.name+' has been turned '+stateStr
        
    def getState(self):
        state = GPIO.input(self.physChanNum)
        self.currentState = state
        return state

    def createInterlock(self,confDict,aiObj,key=None):
        newInterlock = interlock(confDict,aiObj)
        if key is None:
            interlockIndex = len(self.interlocks.keys())
        else:
            interlockIndex = key
        self.interlocks[interlockIndex] = newInterlock
            
    def addInterlock(self,interlock):
        interlockIndex = len(self.interlocks.keys())
        self.interlocks[interlockIndex] = interlock
        
    def deleteInterlock(self,interlockKey):
        del self.interlocks[interlockKey]
        
    def getInterlocks(self):
        return self.interlocks
        
    def setInterlockState(self,newState):
        self.interlockState = newState
        
    def testInterlocks(self):
        if not self.interlockState: return False
        for interlock in self.interlocks.values():
            if interlock.testInterlock():
                print 'INTERLOCK TRIPPED ON '+self.name+'!!!'
                print str(interlock.aiChannelObj.name)+' was measured above setpoint of '+str(interlock.limitValue)+' at '+str(interlock.aiChannelObj.LCD.value())
                return True
        return False

    def configUpdate(self):
        for interlockKey, interlock in self.interlocks.items():
            confDict = interlock.getConfDict()
            interlockKey = str(interlockKey)
            if interlockKey not in self.interlockConfigParser.sections():
                self.interlockConfigParser.add_section(interlockKey)
            self.interlockConfigParser.set(interlockKey, 'senseChan', confDict['senseChan'])
            self.interlockConfigParser.set(interlockKey, 'logFun', confDict['logFun'])
            self.interlockConfigParser.set(interlockKey, 'limVal', str(confDict['limVal']))
        configSectionList = self.interlockConfigParser.sections()
        for configSection in configSectionList:
            if int(configSection) not in self.interlocks.keys():
                self.interlockConfigParser.remove_section(configSection)
        with open(self.interlockConfigFilename, 'wb') as configfile:
            self.interlockConfigParser.write(configfile)



# create interlock object
# upon initialization it takes an analog input channel (e.g. water temp)
# to monitor, a limit value (e.g. 30 degrees). These will not be directly
# initialized but rather created/disabled/destroyed by a digital channel
# object which the interlock can toggle when limit is crossed as per 
# logicalFunction.


# interlocks will be test of the logical form:
# if [AI_CHANNEL] is [LOGICAL_FUNCTION] [LIMITVAL] then turn off


import operator
LOGICAL_FUNCTIONS = {
    '>': operator.gt,
    '>=': operator.ge,
    '<': operator.lt,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne
}

class interlock:
        def __init__(self,confDict,aiObj):
            self.aiChannelName = confDict['senseChan']
            self.logicalFunction = confDict['logFun']
            self.limitValue = confDict['limVal']
            self.aiChannelObj = aiObj
            
        def testInterlock(self):
            function = LOGICAL_FUNCTIONS[self.logicalFunction]  # lookup logical function based on string
            latestReading = self.aiChannelObj.LCD.value()       # get the latest measured value via LCD
            interlockTripped = not function(latestReading,self.limitValue) #e.g. is latest reading greater than setpoint?
            return interlockTripped
            
        def getConfDict(self):
            confDict = {}
            confDict['senseChan'] = self.aiChannelName
            confDict['logFun'] = self.logicalFunction
            confDict['limVal'] = self.limitValue
            return confDict






