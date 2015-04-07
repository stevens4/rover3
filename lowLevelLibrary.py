
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
		


import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)  # use pin numberings printed on cobbler

# create DO channel objects
class doChannel:
	def __init__(self,confDict):
		# read in static class variables
		self.name = confDict['name']
		self.physChanNum = confDict['physicalChannel']
		self.interlocks = {}
		self.currentState = False
		GPIO.setup(self.physChanNum,GPIO.OUT)
		
	def setState(self, newState):
		GPIO.output(self.physChanNum, newState)
		self.currentState = newState
		print 'state on '+self.name+' has been changed to: '+str(newState)
		
	def getState(self):
		state = GPIO.input(self.physChanNum)
		self.currentState = state
		return state
		
	def createInterlock(self,aiChan,limitVal,logicalFunction):
		newInterlock = interlock(aiChan,limitVal,logicalFunction)
		interlockIndex = len(self.interlocks.keys())
		self.interlocks[interlockIndex] = newInterlock
		
	def addInterlock(self,interlock):
		interlockIndex = len(self.interlocks.keys())
		self.interlocks[interlockIndex] = interlock
		
	def deleteInterlock(self,interlockKey):
		del self.interlocks[interlockKey]
		
	def toggleInterlock(self,interlock,newState):
		self.interlocks[interlock].setState(newState)

	def getInterlocks(self):
		return self.interlocks
		
	def testInterlocks(self):
		for interlock in self.interlocks.values():
			if interlock.testInterlock() and interlock.getState():
				print 'interlock tripped on '+self.name
				print str(interlock.aiChannel)+' registered above setpoint: '+str(interlock.getLimitValue())
				self.setState(False)




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
		def __init__(self,aiChan,limitVal,logicalFunctionStr):
			self.aiChannel = aiChan
			self.limitValue = limitVal
			self.logicalFunction = logicalFunctionStr
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
			
		






