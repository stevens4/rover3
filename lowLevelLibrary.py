
from Adafruit_ADS1x15 import ADS1x15 as A2DObject

from functools import partial

# create AI channel objects
class aiChannel:
    def __init__(self,confDict):
        #open connection on physicalChannel
        self.name = confDict['labelText']
        self.i2cAddress = confDict['i2cAddress']
        self.physChan = confDict['physicalChannel']
        self.gain = confDict['gainFactor']
        self.rate = confDict['sampleRate']
        self.LCD = None
        self.mapParams = confDict['mapParams']
        self.units = confDict['mappedUnits']
        self.connection = A2DObject(address=self.i2cAddress)
        self.readOrder = confDict['readOrder']
    
    def getLatestVoltage(self):
        #print self.name, self.i2cAddress, self.physChan    
        return self.connection.readADCSingleEnded( 
            channel=self.physChan, 
            pga=self.gain,
            sps=self.rate
        )
        
    def getNReadings(self,nSamp):
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
    
    def _map(self,rawReading):
        mappedVoltage = self.mapParams[0]
        mappedVoltage += self.mapParams[1]*rawReading
        mappedVoltage += self.mapParams[2]*rawReading**2
        mappedVoltage += self.mapParams[3]*rawReading**3
        mappedVoltage += self.mapParams[4]*rawReading**4
        return mappedVoltage
        
    def getLastReading(self):
        newVoltage = self.getLatestVoltage()
        newReading = self._map(newVoltage)
        if self.LCD is not None:
            self.LCD.display(newReading)
        return newReading
        

from config import roverLogPath
import ConfigParser
import os


import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)  # use pin numberings printed on cobbler

# create DO channel objects
class doChannel:
    def __init__(self,confDict,aiChanDict):
        # read in static class variables
        self.name = confDict['name']
        self.physChanNum = confDict['physicalChannel']
        self.labelText = confDict['labelText']
        self.aiChanDict = aiChanDict
        
        self.currentState = False
        GPIO.setup(self.physChanNum,GPIO.OUT)
        
        initState = confDict['initState'] in ['True']
        self.setState(initState)
        
        self.interlocks = {}
        self.confDict = confDict
        
        # initialize interlock configparser object, read in
        self.interlockConfigParser = ConfigParser.RawConfigParser()
        self.interlockConfigFilename = os.path.join(roverLogPath, 'interlockConfig_'+self.name+'.txt')
        self.interlockConfigParser.read(self.interlockConfigFilename)
        
        
        # parse the interlocks config dicts and create each
        for interlockKey in self.interlockConfigParser.sections():
            thisInterlockConfDict = {}
            thisInterlockConfDict['senseChan'] = self.interlockConfigParser.get(interlockKey, 'senseChan')
            thisInterlockConfDict['logFun'] = self.interlockConfigParser.get(interlockKey, 'logFun')
            thisInterlockConfDict['limVal'] = float(self.interlockConfigParser.get(interlockKey, 'limVal'))
            thisAIChanObj = self.aiChanDict[thisInterlockConfDict['senseChan']]
            thisInterlock = self.createInterlock(thisInterlockConfDict,thisAIChanObj,key=int(interlockKey))
            self.interlocks[int(interlockKey)].setState(bool(self.confDict['initInterlockState']))
        
  
  
    def setState(self, newState):
        GPIO.output(self.physChanNum, newState)
        self.currentState = newState
        print 'state on '+self.name+' has been changed to: '+str(newState)
        
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
        
    def testInterlocks(self):
        for interlock in self.interlocks.values():
            if interlock.testInterlock() and interlock.getState():
                print 'interlock tripped on '+self.name
                print str(interlock.aiChannel)+' registered above setpoint: '+str(interlock.getLimitValue())
                self.setState(False)
    
    def getInterlockState(self):
        if len(self.interlocks.values()) == 0:
            return False
        else:
            firstInterlockState = self.interlocks[0].getState()
            return firstInterlockState
    
    def setAllInterlocksState(self,newState):
        for interlock in self.interlocks.values():
            interlock.setState(newState)
        
    def setInterlockState(self,interlock,newState):
        self.interlocks[interlock].setState(newState)

    def getInterlocks(self):
        return self.interlocks

    def configUpdate(self):
        for interlockKey, interlock in self.interlocks.items():
            confDict = interlock.getConfDict()
            interlockKey = str(interlockKey)
            if interlockKey not in self.interlockConfigParser.sections():
                self.interlockConfigParser.add_section(interlockKey)
            self.interlockConfigParser.set(interlockKey, 'senseChan', confDict['senseChan'])
            self.interlockConfigParser.set(interlockKey, 'logFun', confDict['logFun'])
            self.interlockConfigParser.set(interlockKey, 'limVal', str(confDict['limVal']))
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
            if 'aiChanObj' in confDict.keys():
                self.aiChannelObj = confDict['aiChanObj']
            else:
                self.aiChannelObj = aiObj
            
            self.enabled = False
            
        
        def setState(self,newState):
            self.enabled = newState
            
        def getState(self):
            return self.enabled
            
        def testInterlock(self):
            function = LOGICAL_FUNCTIONS[self.logicalFunction]
            latestReading = self.aiChannelObj.LCD.value()
            interlockTripped = not function(latestReading,self.limitValue)
            if interlockTripped:
                #print "interlock tripped on channel %s! %d is $s the limit of $d." %
                print self.aiChannelName, latestReading, self.logicalFunction, self.limitValue
            return interlockTripped
            
        def getConfDict(self):
            confDict = {}
            confDict['senseChan'] = self.aiChannelName
            confDict['logFun'] = self.logicalFunction
            confDict['limVal'] = self.limitValue
            return confDict






