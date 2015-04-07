
# create AI channel objects
class aiChannel:
    def __init__(self,confDict):
        #open connection on physicalChannel
        self.name = confDict['name']
        self.physChan = confDict['physicalChannel']
        self.scaling = confDict['scaling']
        self.offset = confDict['offset']
    
    def _map(self,rawReading):
        mappedVoltage = self.scaling*rawReading + self.offset
        return mappedVoltage
        
    def getReading(self):
        #measure latest
        return reading
    
    def getNReadings(self,numToRead):
        readings = []
        while len(readings) < numToRead:
            newReading = self.getReading()
            readings.append(newReading)
        return readings
        

from config import roverLogPath
import ConfigParser
import os


# create DO channel objects
class doChannel:
    def __init__(self,confDict):
        #open connection on physicalChannel
        self.name = confDict['name']
        self.physChan = confDict['physicalChannel']
        self.labelText = confDict['labelText']
        self.enabled = confDict['initState'] in ['True']
        
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
            thisInterlock = self.createInterlock(thisInterlockConfDict,key=int(interlockKey))
            self.interlocks[int(interlockKey)].setState(bool(self.confDict['initInterlockState']))
        
    def setState(self, newState):
        #self.physChan.write(newState)
        self.enabled = newState
        print 'state on '+self.name+' has been changed to: '+str(self.enabled)
        
    def getState(self):
        #state = self.physChan.read()
        return self.enabled
        
    def createInterlock(self,confDict,key=None):
        newInterlock = interlock(confDict)
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
        
    def testInterlocks(self):
        for interlock in self.interlocks.values():
            if interlock.testInterlock() and interlock.getState():
                print 'interlock tripped on '+self.name
                print str(interlock.aiChannel)+' registered above setpoint: '+str(interlock.getLimitValue())
                self.setState(False)

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
        def __init__(self,confDict):
            self.aiChannel = confDict['senseChan']
            self.limitValue = confDict['limVal']
            self.logicalFunction = confDict['logFun']
            self.enabled = True
        
        def setState(self,newState):
            self.enabled = newState
            
        def getState(self):
            return self.enabled
            
        def setSenseChannel(self,aiChan):
            self.aiChannel = aiChan
            
        def getSenseChannel(self):
            return self.aiChannel  #.name
            
        def setLimitValue(self,limitVal):
            self.limitValue = limitVal
            
        def getLimitValue(self):
            return self.limitValue
            
        def setLogicalFunction(self,logFunc):
            self.logicalFunction = logFunc
            
        def getLogicalFunction(self):
            return self.logicalFunction
            
        def testInterlock(self):
            function = LOGICAL_FUNCTIONS[self.logicalFunctionStr]
            latestReading = self.aiChannel.getReading()
            interlockTripped = function(latestReading,self.limitValue)
            return interlockTripped
            
        def getConfDict(self):
            confDict = {}
            confDict['senseChan'] = self.getSenseChannel()
            confDict['logFun'] = self.getLogicalFunction()
            confDict['limVal'] = self.getLimitValue()
            return confDict






